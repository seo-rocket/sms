import django_filters
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from django.shortcuts import render
from django.views.generic import ListView
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

from datetime import date
from django.core.paginator import Paginator


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
    # Получаем фильтр по дате, если он указан
    date_filter = request.GET.get('date_filter', None)

    # Фильтрация сообщений по дате, если выбран фильтр
    if date_filter:
        sms_list = SMS.objects.filter(received_at__date=date_filter).order_by('-received_at')
        total_sms_for_day = sms_list.count()  # Количество сообщений за выбранный день
    else:
        sms_list = SMS.objects.all().order_by('-received_at')  # Сортировка по убыванию даты
        total_sms_for_day = 0  # Если дата не выбрана, то нет сообщений за день

    # Получаем общее количество всех сообщений
    total_sms = SMS.objects.count()  # Это общее количество SMS за все время, не зависимо от фильтра

    # Получаем статистику по регионам для сообщений, отфильтрованных по дате
    if date_filter:
        region_counts = SMS.objects.filter(received_at__date=date_filter).values('region').annotate(count=Count('region'))
    else:
        region_counts = SMS.objects.values('region').annotate(count=Count('region'))

    # Пагинация: отображаем максимум 100 сообщений на странице
    paginator = Paginator(sms_list, 100)
    page_number = request.GET.get('page')
    sms_list = paginator.get_page(page_number)

    # Общая статистика
    total_services = Service.objects.count()
    total_accounts = Account.objects.count()

    # Статистика по сервисам с фильтрацией по дате
    if date_filter:
        # Теперь фильтруем все сообщения за выбранную дату и аннотируем их по сервисам
        service_counts = Service.objects.filter(sms__received_at__date=date_filter).annotate(count=Count('sms'))
    else:
        service_counts = Service.objects.annotate(count=Count('sms'))

    # Статистика по аккаунтам с фильтрацией по дате
    context = {
        'sms_list': sms_list,
        'total_sms': total_sms,
        'total_sms_for_day': total_sms_for_day,
        'total_services': total_services,
        'total_accounts': total_accounts,
        'region_counts': region_counts,
        'service_counts': service_counts,
        'date_filter': date_filter
    }

    return render(request, 'index.html', context)




