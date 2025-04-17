from django.shortcuts import render
from Supplier.models import *
from Customer.models import * 
# Create your views here.
def Supp_Home(request):
    return render(request,'Home.html')

def earning(request):
    
    return render(request,'Earning.html')

def order(request):
    return render(request,'Order.html')

def order_list(request):
    if request.method=='GET':
        users = UserDetail.objects.select_related('location').first()
        orders = TankerDetail.objects.first() 

        user_name=f"{users.first_name} {users.last_name}"
        size=orders.capacity
        cag=orders.category
        cust_number=users.phone_number
        location=f"{users.location.address_line}, {users.location.city}" if users.location else "N/A"

        my_detail = {
            'user_name':user_name,
            'size':size,
            'cag':cag,
            'cust_number':cust_number,
            'location':location,
        }
    else:
        my_detail = {
            'user_name': 'N/A',
            'size': 'N/A',
            'cag': 'N/A',
            'cust_number': 'N/A',
            'location': 'N/A',
        }
    
    return render(request,'Order_List.html',context=my_detail)

def notification(request):
    return render(request,'Notification.html')

def profile(request):
    if request.method=="GET":
        supp_name = DriverDetail.objects.select_related().first()
        feedback = Feedback.objects.select_related().first()

        context = {
            'name':f"{supp_name.user.first_name} {supp_name.user.last_name}" if supp_name else 'N/A',
            'location':supp_name.user.location.city,
            'phone': supp_name.user.phone_number,
            'rating': feedback.rating_value,    
        }
    return render(request,'Profile.html',context)