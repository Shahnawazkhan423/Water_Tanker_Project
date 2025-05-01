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
    path('Registers/',views.register_view,name="Register_page"),
    path('Tanker_Detail/',views.tanker_detail_view,name="tanker_detail"),
    path('Login/',views.login_view,name="Login_page"),
    path('Logout/',views.logout_view,name="Logout_page"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)