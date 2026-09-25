from django.urls import path
from . import views

urlpatterns = [
    # User Authentication & Password Reset
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
    path('password-reset/', views.user_password_reset, name='user_password_reset'),
    path('password-reset/done/', views.user_password_reset_done, name='user_password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.user_password_reset_confirm, name='user_password_reset_confirm'),
]
