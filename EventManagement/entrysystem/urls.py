from django.urls import path
from .views import register, login, payments, check_jwt, profile, profile_checker, health_check, validate_qr, analytics, validate_dynamic_qr, freeze_operations, get_flag

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('payments/', payments, name='payments'),
    path('check_jwt/', check_jwt, name='check_jwt'),
    path('profile/', profile, name='profile'),
    path('profile_checker/', profile_checker, name='profile_checker'),
    path('health_check/', health_check, name='health_check'),
    path('validate_qr/', validate_qr, name='validate_qr'),
    path('analytics/', analytics, name='analytics'),
    path('validate_dynamic_qr/', validate_dynamic_qr, name='validate_dynamic_qr'),
    path('freeze_operations/', freeze_operations, name='freeze_operations'),
    path('get_flag/', get_flag, name='get_flag')
]
