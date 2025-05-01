from django.shortcuts import render,redirect
from Supplier.models import *
from Customer.models import *
from Supplier.forms import*
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

# Create your views here.
def register_view(request):
    if request.method=="POST":
        user_form = SupplierDetailForm(request.POST)
        location_form = SupplierLocationDetailForm(request.POST)
        if user_form.is_valid() and location_form.is_valid():
            location = location_form.save()
            user = user_form.save()
            user.location = location
            user.password = make_password(user.password)
            user.save()
            return redirect('tanker_detail')
    else:
        user_form = SupplierDetailForm()
        location_form = SupplierLocationDetailForm()

    return render(request, 'Register.html', {'user_form': user_form, 'location_form': location_form})


def tanker_detail_view(request):
    if request.method=="POST":
        document = WaterTankerForm(request.POST,request.FILES)  
        tanker_detail = SupplierTankerDetailForm(request.POST)
        if document.is_valid and tanker_detail.is_valid():
            tanker_instance  = document.save()
            tanker_detail_instance = tanker_detail.save(commit=False)
            tanker_detail_instance.tanker_instance = tanker_instance
            tanker_detail_instance.save()
            messages.success(request, 'Registration successful.')
            return redirect('Login_page')
    else:
        document = WaterTankerForm()
        tanker_detail = SupplierTankerDetailForm()

    return render(request,"tanker_detail.html",{'document': document,
        'tanker_detail': tanker_detail})

def login_view(request):
    if request.method=="POST":
        email = request.POST.get("email")
        print(email)
        password = request.POST.get("passwords")
        print(password)
        user = authenticate(request, email=email, password=password)
        print(user) 
       
        if user is not None and isinstance(user, SupplierUser):
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('Login_page')

    return render(request,"Login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('Login_page')

@login_required(login_url="Login_page")
def Supp_Home(request):
    return render(request,'Home.html')

@login_required(login_url="Login_page")
def earning(request):
    return render(request,'Earning.html')

@login_required(login_url="Login_page")
def order(request):
    return render(request,'Order.html')

@login_required(login_url="Login_page")
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

@login_required(login_url="Login_page")
def notification(request):
    return render(request,'Notification.html')

@login_required(login_url="Login_page")
def profile(request):
    return render(request,'Profile.html')