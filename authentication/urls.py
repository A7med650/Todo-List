from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('activate-user/<uidb64>/<token>',
         views.activate_user, name='activate'),
]
