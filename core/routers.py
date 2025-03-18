from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'services', ServiceViewSet)
router.register(r'sms', SMSViewSet)
router.register(r'accounts', AccountViewSet)

