from django.shortcuts import render,redirect
from Supplier.models import *
from Customer.models import *
from Customer.forms import UserDetailForm, TankerDetailForm,LocationDetailForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

# Create your views here.
def register_view(request):
    if request.method=="POST":
        user_form = UserDetailForm(request.POST)
        location_form = LocationDetailForm(request.POST)
        if user_form.is_valid() and location_form.is_valid():
            location = location_form.save()
            user = user_form.save()
            user.location = location
            user.password = make_password(user.password)
            user.save()
            messages.success(request, 'Registration successful.')
            return redirect('tanker_detail')
    else:
        user_form = UserDetailForm()
        location_form = LocationDetailForm()

    return render(request, 'Register.html', {'user_form': user_form, 'location_form': location_form})


def tanker_detail_view(request):
    return render(request,"tanker_detail.html")

def login_view(request):
    return render(request,"login.html")

def logout_view(request):
    return render(request,"logout.html")

@login_required(login_url="login")
def Supp_Home(request):
    return render(request,'Home.html')

@login_required(login_url="login")
def earning(request):
    return render(request,'Earning.html')

@login_required(login_url="login")
def order(request):
    return render(request,'Order.html')

@login_required(login_url="login")
def order_list(request):
    if request.method=='GET':
        users = CustomUser.objects.select_related('location').first()
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

@login_required(login_url="login")
def notification(request):
    return render(request,'Notification.html')

@login_required(login_url="login")
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