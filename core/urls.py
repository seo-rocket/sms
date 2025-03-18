from django.urls import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.db.models import Q
from django.urls import path

from core.views import *

app_name = 'core'



urlpatterns = [
    re_path(r'^$', index, name='index'),
    re_path(r'^about/$', about, name='about'),
    re_path(r'^contacts/$', contacts, name='contacts'),
    re_path(r'^news/$', news, name='news'),
    re_path(r'^news/(?P<alias>[0-9A-Za-z\-_]+)/$', news_item, name='news-item'),
    re_path(r'^reviews/$', reviews, name='reviews'),
    re_path(r'^ajax/$', ajax, name='ajax'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
