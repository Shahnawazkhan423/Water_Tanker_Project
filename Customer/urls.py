from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('Booking/',views.booking,name='booking'),
    path('Driver_Detail/',views.driver_detail,name='driver_detail'),
    path('Profile/',views.profile,name='profile'),
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('notification/delete/<int:id>/', views.delete_notification, name='delete_notifications'),
    path('Notifications/', views.notification, name='notification'),
    path('Register/',views.register_view,name='register'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='customer_cancel_order'),
    path('Login/',views.login_view,name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<token>/', views.reset_password, name='reset_password'),
    path('Logout/',views.logout_view,name='logout'),
]
