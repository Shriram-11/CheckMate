from django.urls import path
from .views import signup, login, payments, check_jwt

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('payments/', payments, name='payments'),
    path('check_jwt/', check_jwt, name='check_jwt'),


]
