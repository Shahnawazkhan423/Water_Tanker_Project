from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views
urlpatterns=[
    path('Home_Page/',views.Supp_Home,name='Home'),
    path('Earning/',views.earning,name='Earning'),
    path('Order/',views.order_list,name='Order_List'),
    path('Notifications/',views.notification,name='Notification'),
    path('Profile/',views.profile,name='Profile'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)