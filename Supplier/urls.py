from django.urls import path 
from . import views
urlpatterns=[
    path('Home_Page/',views.Supp_Home,name='Home'),
    path('Earning/',views.earning,name='Earning'),
    path('Order/',views.order_list,name='Order_List'),
    path('Notifications/',views.notification,name='Notification'),
    path('Profile/',views.profile,name='Profile')
]