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





def index(request):
    # Получаем фильтр по дате, если он указан
    date_filter = request.GET.get('date_filter', None)
    
    # Фильтрация сообщений по дате, если выбран фильтр
    if date_filter:
        sms_list = SMS.objects.filter(received_at__date=date_filter)
    else:
        sms_list = SMS.objects.all()

    # Общая статистика
    total_sms = sms_list.count()
    total_services = Service.objects.count()
    total_accounts = Account.objects.count()

    # Количество SMS по регионам
    region_counts = SMS.objects.values('region').annotate(count=Count('region'))

    # Статистика по сервисам
    service_counts = Service.objects.annotate(count=Count('sms'))

    context = {
        'sms_list': sms_list,
        'total_sms': total_sms,
        'total_services': total_services,
        'total_accounts': total_accounts,
        'region_counts': region_counts,
        'service_counts': service_counts,
        'date_filter': date_filter
    }

    return render(request, 'index.html', context)