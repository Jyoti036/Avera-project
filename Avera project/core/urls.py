from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('adoption-info/', views.adoption_info, name='adoption_info'),
    path('wishlists/', views.wishlist_catalog, name='wishlists'),
    path('stories/', views.success_stories, name='success_stories'),
    path('faqs/', views.faqs_view, name='faqs'),
    path('about/', views.about_avera, name='about'),

    # User Dashboard & Gift Actions
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('pledge-gift/', views.pledge_gift, name='pledge_gift'),
    path('pledge-gift/<int:wishlist_id>/', views.pledge_gift, name='pledge_gift_item'),
    path('notifications/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),

    # Admin Portal Management (Accessible only to logged in Admin)
    path('admin-portal/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/gifts/', views.admin_manage_gifts, name='admin_manage_gifts'),
    path('admin-portal/gifts/<int:gift_id>/update/', views.admin_update_gift_status, name='admin_update_gift_status'),
    path('admin-portal/children/', views.admin_manage_children, name='admin_manage_children'),
    path('admin-portal/wishlists/', views.admin_manage_wishlists, name='admin_manage_wishlists'),
]
