from django.shortcuts import render,redirect,get_object_or_404
from Supplier.models import *
from Customer.models import *
from Supplier.forms import*
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from notifications.models import Notification
from django.http import JsonResponse
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
        if document.is_valid() and tanker_detail.is_valid():
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


@login_required
def toggle_availability(request):
    if request.method == 'POST':
        supplier = request.user
        supplier.is_available = not supplier.is_available
        supplier.save()
        return JsonResponse({'status': 'success', 'is_available': supplier.is_available})
    return JsonResponse({'status': 'error'}, status=400)

@login_required(login_url="Login_page")
def Supp_Home(request):
    return render(request,'Home.html')

@login_required(login_url="Login_page")
def earning(request):
    return render(request,'Earning.html')

@login_required(login_url="Login_page")
def order(request, order_id):
    order = get_object_or_404(OrderDetail, id=order_id, driver__user=request.user)
    
    # Mark this order as accepted
    order.order_status = 'Accepted'
    order.save()
    
    # Mark all other pending orders for this customer as rejected
    OrderDetail.objects.filter(
        user=order.user,
        order_status='Pending'
    ).exclude(id=order_id).update(order_status='Rejected')
    
    # Create notification for customer
    Notification.objects.create(
        recipient=order.user,
        sender=request.user,
        message=f"Your order #{order.id} has been accepted by {request.user.first_name}",
        notification_type='order_accepted',
        order_id=order.id
    )
    
    messages.success(request, "Order accepted successfully!")
    return redirect('Order_List')

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

@login_required(login_url="Login_page")
def update_order_status(request, order_id, status):
    order = get_object_or_404(OrderDetail, id=order_id)
    if status == 'cancel':
        order.status = 'Canceled'
        message = f"Your order #{order.id} has been canceled."
        notification_type = 'order_canceled'
    elif status == 'on_way':
        order.status = 'On the Way'
        message = f"Your order #{order.id} is on the way."
        notification_type = 'order_on_way'
    elif status == 'complete':
        order.status = 'Delivered'
        message = f"Your order #{order.id} has been delivered."
        notification_type = 'order_completed'
    
    order.save()
    
    # Create notification for customer
    Notification.objects.create(
        recipient=order.customer_user,  # Adjust based on your model
        sender=request.user,
        message=message,
        notification_type=notification_type,
        order_id=order.id
    )
    
    return redirect('Order_list')

@login_required(login_url="Login_page")
def order_detail(request, order_id):
    order = get_object_or_404(TankerDetail, id=order_id)
    
    # Mark notification as read if exists
    Notification.objects.filter(
        order_id=order_id,
        recipient=request.user
    ).update(is_read=True)
    
    return render(request, 'Order_List.html', {'order': order})