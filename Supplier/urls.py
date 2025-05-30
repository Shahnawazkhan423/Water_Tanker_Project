from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from Supplier import views
urlpatterns=[
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
    path('Home_Page/',views.Supp_Home,name='Home'),
    path('Earning/',views.earning,name='Earning'),
    path('Order/',views.order_list,name='Order_List'),
    path('supplier/notification/delete/<int:id>/', views.delete_notification, name='delete_notification'),
    path('order/update/<int:order_id>/<str:status>/', views.update_order_status, name='supplier_update_order_status'),
    path('Notifications/',views.notification,name='Notification'),
    path('Profile/',views.profile,name='Profile'),
    path('Registers/',views.register_view,name="Register_page"),
    path('Tanker_Detail/',views.tanker_detail_view,name="tanker_detail"),
    path('Login/',views.login_view,name="Login_page"),
    path('Logout/',views.logout_view,name="Logout_page"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)