import django_filters
from django_filters import rest_framework as filters
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import *
from django.utils.timezone import localdate
from .serializers import *
from django.shortcuts import render
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Avg
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
from datetime import date
from django.core.paginator import Paginator
from django.db.models.functions import ExtractHour, TruncDate
from django.utils import timezone
from datetime import timedelta
import json
from datetime import datetime

class UserFilter(filters.FilterSet):
    username = django_filters.CharFilter(field_name="username")

    class Meta:
        model = User
        fields = ['username']

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    # permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = UserFilter

    def get_queryset(self):
        return User.objects.all()

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class SMSViewSet(viewsets.ModelViewSet):
    queryset = SMS.objects.all()
    serializer_class = SMSSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer





# Декоратор для проверки, является ли пользователь администратором
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='/admin/login/')(view_func)


@admin_required
def index(request):
    date_filter = request.GET.get('date_filter', None)
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    if date_filter:
        # Если передан параметр фильтрации даты, используем его
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        except ValueError:
            filter_date = today  # Если формат даты неверный, используем сегодняшнюю дату
        sms_list = SMS.objects.filter(received_at__date=filter_date).order_by('-received_at')
        total_sms_for_day = sms_list.count()
        filter_date_for_hourly = filter_date
    else:
        # Если фильтр не передан, показываем все SMS для списка, но почасовые данные - только за сегодня
        sms_list = SMS.objects.all().order_by('-received_at')
        filter_date_for_hourly = today
        total_sms_for_day = SMS.objects.filter(received_at__date=today).count()

    # Пагинация
    paginator = Paginator(sms_list, 10)  # 10 объектов на страницу
    page_number = request.GET.get('page', 1)  # Если параметр page отсутствует, ставим номер 1

    # Убедимся, что page_number является валидным числом больше 0
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        # Если номер страницы выходит за пределы, показываем последнюю страницу
        page_obj = paginator.get_page(paginator.num_pages)

    # Расчет диапазона страниц для отображения в пагинации
    page_range = calculate_page_range(page_obj.number, paginator.num_pages)

    total_sms = SMS.objects.count()

    # Подготовка данных для графиков
    # Данные по регионам
    region_stats = SMS.objects.values('region').annotate(count=Count('region'))
    region_labels = [stat['region'] for stat in region_stats]
    region_data = [stat['count'] for stat in region_stats]

    # Данные по сервисам
    service_stats = Service.objects.annotate(sms_count=Count('sms'))
    service_labels = [service.name for service in service_stats]
    service_data = [service.sms_count for service in service_stats]

    # Почасовая статистика - всегда за текущую дату или выбранную дату
    hourly_stats = SMS.objects.filter(received_at__date=filter_date_for_hourly)\
        .annotate(hour=ExtractHour('received_at'))\
        .values('hour')\
        .annotate(count=Count('id'))\
        .order_by('hour')

    # Создадим полный список часов от 0 до 23 с нулевыми значениями для часов, когда нет SMS
    full_hourly_data = {hour: 0 for hour in range(24)}
    for stat in hourly_stats:
        full_hourly_data[stat['hour']] = stat['count']

    hourly_labels = [f"{hour}:00" for hour in range(24)]
    hourly_data = [full_hourly_data[hour] for hour in range(24)]

    # Timeline данные (за последние 7 дней)
    timeline_stats = SMS.objects.filter(received_at__gte=week_ago)\
        .annotate(date=TruncDate('received_at'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')

    timeline_labels = [stat['date'].strftime('%Y-%m-%d') for stat in timeline_stats]
    timeline_data = [stat['count'] for stat in timeline_stats]

    service_details = []
    for service in service_stats:
        # За сегодня
        today_count = SMS.objects.filter(service=service, received_at__date=today).count()

        # За неделю
        week_count = SMS.objects.filter(service=service, received_at__gte=week_ago).count()

        # За месяц
        month_count = SMS.objects.filter(service=service, received_at__gte=month_ago).count()

        # Частота SMS по часам (для простоты, выводим среднее количество SMS по часу)
        hourly_rate = SMS.objects.filter(service=service)\
            .annotate(hour=ExtractHour('received_at'))\
            .values('hour')\
            .annotate(count=Count('id'))\
            .aggregate(avg_hourly=Avg('count'))['avg_hourly'] or 0

        service_details.append({
            'name': service.name,
            'sms_count': service.sms_count,
            'today_count': today_count,
            'week_count': week_count,
            'month_count': month_count,
            'hourly_rate': hourly_rate,
            'id': service.id,
            'frequency_class': 'high' if hourly_rate > 5 else 'low'  # Пример условного класса для частоты
        })

    context = {
        'sms_list': page_obj,
        'page_range': page_range,  # Добавляем диапазон страниц для пагинации
        'total_sms': total_sms,
        'total_sms_for_day': total_sms_for_day,
        'total_services': Service.objects.count(),
        'total_accounts': Account.objects.count(),
        'region_counts': region_stats,
        'service_details': service_details,  # передаем агрегированные данные
        'date_filter': date_filter if date_filter else today.strftime('%Y-%m-%d'),  # Если фильтр не передан, показываем сегодняшнюю дату
        'current_date': today,
        # Данные для графиков
        'region_labels': json.dumps(region_labels),
        'region_data': json.dumps(region_data),
        'service_labels': json.dumps(service_labels),
        'service_data': json.dumps(service_data),
        'hourly_labels': json.dumps(hourly_labels),
        'hourly_data': json.dumps(hourly_data),
        'timeline_labels': json.dumps(timeline_labels),
        'timeline_data': json.dumps(timeline_data),
    }

    return render(request, 'index.html', context)


def calculate_page_range(current_page, total_pages, show_adjacent=2):
    """
    Рассчитывает диапазон страниц для отображения в пагинации.

    Args:
        current_page: Текущая страница
        total_pages: Общее количество страниц
        show_adjacent: Количество страниц для отображения до и после текущей

    Returns:
        list: Список номеров страниц для отображения
    """
    if total_pages <= 5 + (show_adjacent * 2):
        # Если общее количество страниц небольшое, показываем все
        return range(1, total_pages + 1)

    # Всегда включаем первую и последнюю страницу
    page_range = []

    # Рассчитываем диапазон вокруг текущей страницы
    left_index = max(1, current_page - show_adjacent)
    right_index = min(current_page + show_adjacent, total_pages)

    # Добавляем первую страницу и многоточие слева (если нужно)
    if left_index > 2:
        page_range.extend([1, None])  # None будет заменено на многоточие в шаблоне
    elif left_index == 2:
        page_range.append(1)

    # Добавляем страницы вокруг текущей
    page_range.extend(range(left_index, right_index + 1))

    # Добавляем многоточие и последнюю страницу (если нужно)
    if right_index < total_pages - 1:
        page_range.extend([None, total_pages])  # None будет заменено на многоточие в шаблоне
    elif right_index == total_pages - 1:
        page_range.append(total_pages)

    return page_range
