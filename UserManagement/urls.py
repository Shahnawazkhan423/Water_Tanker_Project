from django.urls import path
from Supplier import views as supplier_views
from Customer import views as customer_views

urlpatterns = [

    path('register/', customer_views.register_view, name='register'),
    path('login/', customer_views.login_view, name='login'),

    # Supplier Routes
    path('supplier/register/', supplier_views.register_view, name='Register_page'),
    path('supplier/login/', supplier_views.login_view, name='Login_page'),
]
