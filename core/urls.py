from django.urls import re_path, path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import *
from core.routers import router  # Подключаем ваш роутер для API

app_name = 'core'

urlpatterns = [
    # Корневые маршруты
    path('', index, name="index"),
#    path('sms-list/', sms_list, name="sms_list"),  # Включаем маршруты AP

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
