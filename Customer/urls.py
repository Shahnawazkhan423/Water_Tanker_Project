from django.urls import path
from . import views

urlpatterns = [
    path('Home/',views.home,name='home'),
    path('Booking/',views.booking,name='booking'),
    path('Driver_Detail/',views.driver_detail,name='driver_detail'),
    path('Profile/',views.profile,name='profile'),
    path('Notifications/',views.notification,name='notification')
]
