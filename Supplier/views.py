from django.shortcuts import render,redirect,get_object_or_404
from Supplier.models import *
from Customer.models import *
from Supplier.forms import SupplierRegistrationForm,SupplierLocationDetailForm,SupplierTankerDetailForm,WaterTankerForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import datetime
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.hashers import make_password

def register_view(request):
    if request.method == "POST":
        user_form = SupplierRegistrationForm(request.POST, request.FILES)
        location_form = SupplierLocationDetailForm(request.POST)
        
        if user_form.is_valid() and location_form.is_valid():
            print("Forms are valid")
            location = location_form.save()

            user = user_form.save(commit=False)
            user.location = location
            user.save()

            user.password = make_password(user_form.cleaned_data['password'])
            user.save()

            messages.success(request, 'Registration successful.')
            return redirect('tanker_detail')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = SupplierRegistrationForm()
        location_form = SupplierLocationDetailForm()

    return render(request, 'Register.html', {
        'user_form': user_form,
        'location_form': location_form
    })
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
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, "Login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return render(request, "Login.html")


@login_required(login_url="Login_page")
def toggle_availability(request):
    if request.method == 'POST':
        supplier = request.user
        supplier_profile = supplier.supplier
        new_status = not supplier_profile.is_available
        supplier_profile.is_available = new_status
        supplier_profile.save()

        if new_status:
            DriverAvailability.objects.create(
                user=supplier_profile,
                availability_date=timezone.now().date(),
                start_time=timezone.now().time(),
                status='available'
            )
        else:
            last_log = DriverAvailability.objects.filter(user=supplier_profile, status='available').last()
            if last_log:
                last_log.end_time = timezone.now().time()
                last_log.status = 'unavailable'
                last_log.save()

        return JsonResponse({'status': 'success', 'is_available': new_status})
@login_required(login_url="Login_page")
def get_supplier_dashboard_data(user):
    data = {
        'orders_accept': 0,
        'orders_complete': 0,
        'total_revenue': 0,
        'orders_today': []
    }

    driver = DriverDetail.objects.filter(user=user).first()
    if not driver:
        return data

    today = datetime.today()

    orders_today = OrderDetail.objects.filter(
        driver=driver,
        order_date__year=today.year,
        order_date__month=today.month,
        order_date__day=today.day
    )

    data['orders_today'] = orders_today
    data['total_revenue'] = orders_today.aggregate(total=Sum('price'))['total'] or 0
    data['orders_accept'] = OrderDetail.objects.filter(order_status='Accepted', driver=driver).count()
    data['orders_complete'] = OrderDetail.objects.filter(order_status='Delivered', driver=driver).count()

    return data

@login_required(login_url="Login_page")
def Supp_Home(request):
    if request.user.user_type == 'supplier':
        return render(request,'Home.html')
    else:
        messages.error(request, "This user does not exist or is not a supplier.")
        return render(request,"Login.html")

@login_required(login_url="Login_page")
def earning(request):
    return render(request,'Earning.html')

@login_required(login_url="Login_page")
def order(request,order_id):
    driver = getattr(request.user, 'driver', None)
    order = get_object_or_404(OrderDetail, id=order_id, driver=driver)
    
    if request.method =="POST":
        status = request.POST.get('status')
        if status == 'accept': 
            order.order_status = 'Accepted'
            order.driver = driver
            order.save()

            Notification.objects.create(
                recipient=order.user,
                sender=request.user,
                message=f"Your order #{order.id} has been accepted by {request.user.first_name}",
                notification_type='order_accepted',
                order_id=order.id
            )

            messages.success(request, "Order accepted successfully!")
            return redirect('Order_List')
        else:
            return redirect("Home")
    return render(request, 'Order.html', {'order': order})

@login_required(login_url="Login_page")
def order_list(request):
    driver = None
    if request.user.is_authenticated:
        driver = DriverDetail.objects.filter(user=request.user).first()
    
    orders = OrderDetail.objects.none()
    if request.method == 'GET' and driver:
        orders = OrderDetail.objects.filter(
            order_status='Accepted',
            driver=driver,  
        ).select_related('user', 'location', 'driver', 'tanker')
        context = {'orders': orders}

    else:
        context = {
            'orders': None,
        }
    return render(request, 'Order_List.html', context)

@login_required(login_url="Login_page")
def notification(request):
    notifications = Notification.objects.filter(customer=request.user).order_by('-timestamp')
    return render(request,'Notification.html',{'notifications':notifications})

@login_required(login_url="Login_page")
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'Profile.html', {'user': request.user})
    else:
        return redirect('login')

@login_required(login_url="Login_page")
def update_order_status(request, order_id, status):
    order = get_object_or_404(OrderDetail, id=order_id)
    if status == 'cancel':
        order.status = 'Canceled'
        message = f"Your order #{order.id} has been canceled."
    elif status == 'accept':
        order.status = 'Accepted'
        message = f"Your order #{order.id} has been accepted."
    elif status == 'on_way':
        order.status = 'On the Way'
        message = f"Your order #{order.id} is on the way."
    elif status == 'complete':
        order.status = 'Delivered'
        message = f"Your order #{order.id} has been delivered."

    order.save()
    Notification.objects.create(
        recipient=order.user,  
        sender=request.user,
        message=message,
        id=order.id
    )
    
    return redirect('Order_list')

def delete_notification(request, id):
    notif = get_object_or_404(Notification, id=id)
    notif.delete()
    return redirect('Notification')