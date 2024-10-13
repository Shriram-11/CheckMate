from django.urls import path
from .views import register, login, payments, check_jwt, profile, profile_checker

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('payments/', payments, name='payments'),
    path('check_jwt/', check_jwt, name='check_jwt'),
    path('profile/', profile, name='profile'),
    path('profile_checker/', profile_checker, name='profile_checker'),


]
