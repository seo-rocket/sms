from django.contrib import admin
from .models import *

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)

class SMSAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'service', 'received_at')
    search_fields = ('phone_number', 'service__name')
    list_filter = ('service', 'received_at')

class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number')
    search_fields = ('username', 'email', 'phone_number')

admin.site.register(Service, ServiceAdmin)
admin.site.register(SMS, SMSAdmin)
admin.site.register(Account, AccountAdmin)

