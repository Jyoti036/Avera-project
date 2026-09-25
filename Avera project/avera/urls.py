from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    # Standard Django Admin
    path('django-admin/', admin.site.urls),

    # User Accounts & Authentication (Publicly visible options)
    path('accounts/', include('accounts.urls')),

    # Secret / Hidden Admin Portal Authentication
    # (Notice: links to these pages are NOT displayed anywhere on the public navbar/footer)
    path('admin-portal/login/', account_views.admin_login, name='admin_login'),
    path('admin-portal/register/', account_views.admin_register, name='admin_register'),
    path('admin-portal/logout/', account_views.admin_logout, name='admin_logout'),
    path('admin-portal/password-reset/', account_views.admin_password_reset, name='admin_password_reset'),
    path('admin-portal/password-reset/done/', account_views.admin_password_reset_done, name='admin_password_reset_done'),
    path('admin-portal/password-reset-confirm/<uidb64>/<token>/', account_views.admin_password_reset_confirm, name='admin_password_reset_confirm'),

    # Core Application & AVERA Platform routes
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
