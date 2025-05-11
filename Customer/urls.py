from django.urls import path
from . import views

urlpatterns = [
    path('Home/',views.home,name='home'),
    path('Booking/',views.booking,name='booking'),
    path('Driver_Detail/',views.driver_detail,name='driver_detail'),
    path('Profile/',views.profile,name='profile'),
    path('Notifications/', views.notification_view, name='notification'),
    path('order/cancel/<int:order_id>/', views.customer_cancel_order, name='customer_cancel_order'),
    path('Notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('Register/',views.register_view,name='register'),
    path('Login/',views.login_view,name='login'),
    path('Logout/',views.logout_view,name='logout'),
]
