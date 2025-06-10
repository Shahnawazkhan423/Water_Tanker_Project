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
from datetime import timedelta
from geopy.distance import geodesic

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
            SupplierProfile.objects.create(
                user=user,
                location=location,
                is_available=False
            )
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
    if request.method == "POST":
        document_form = WaterTankerForm(request.POST, request.FILES)
        tanker_detail_form = SupplierTankerDetailForm(request.POST)

        if document_form.is_valid() and tanker_detail_form.is_valid():
            document_instance = document_form.save()

            try:
                supplier_profile = request.user.supplier
            except Exception:
                messages.error(request, "You must be registered as a supplier to add tanker details.")
                return redirect('Login_page')

            try:
                driver = DriverDetail.objects.get(user=supplier_profile)
            except DriverDetail.DoesNotExist:
                messages.error(request, "Driver details not found.")
                return redirect('tanker_detail')

            try:
                DriverAvailability.objects.filter(
                    user=supplier_profile,
                    status='available'
                ).latest('availability_date')
                availability_status = True
            except DriverAvailability.DoesNotExist:
                availability_status = False

            TankerDetail.objects.create(
                driver=driver,
                document=document_instance,
                capacity=tanker_detail_form.cleaned_data['capacity'],
                category=tanker_detail_form.cleaned_data['category'],
                available=availability_status
            )

            messages.success(request, 'Tanker registration successful.')
            return redirect('Login_page')
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        document_form = WaterTankerForm()
        tanker_detail_form = SupplierTankerDetailForm()

    return render(request, "tanker_detail.html", {
        'document': document_form,
        'tanker_detail': tanker_detail_form
    })
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
            availability  =DriverAvailability.objects.create(
                user=supplier_profile,
                availability_date=timezone.now().date(),
                start_time=timezone.now().time(),
                status='available'
            )
            try:
                driver_detail = DriverDetail.objects.get(user=supplier_profile)
                driver_detail.availability = availability
                driver_detail.save()
            except DriverDetail.DoesNotExist:
                DriverDetail.objects.create(user=supplier_profile, availability=availability)
            
        else:
            last_log = DriverAvailability.objects.filter(user=supplier_profile, status='available').last()
            if last_log:
                last_log.end_time = timezone.now().time()
                last_log.status = 'unavailable'
                last_log.save()

        return JsonResponse({'status': 'success', 'is_available': new_status})
@login_required(login_url="Login_page")
def get_supplier_dashboard_data(request,user):
    
    data = {
        'orders_accept': 0,
        'orders_complete': 0,
        'total_revenue': 0,
        'orders_today': []
    }

    # Get SupplierProfile from CustomUser
    supplier_profile = getattr(user, 'supplier', None)
    print("THis:====",supplier_profile)
    if not supplier_profile:
        return data

    supplier_profile = request.user.supplier
    driver = DriverDetail.objects.filter(user=supplier_profile).first()
    if not driver:
        return data

    today = datetime.today()

    orders_today = OrderDetail.objects.filter(
        driver=driver,
        order_date__date=today.date()
    )

    data['orders_today'] = orders_today
    data['total_revenue'] = orders_today.aggregate(total=Sum('price'))['total'] or 0
    data['orders_accept'] = OrderDetail.objects.filter(order_status='Accepted', driver=driver).count()
    data['orders_complete'] = OrderDetail.objects.filter(order_status='Delivered', driver=driver).count()

    return data

@login_required(login_url="Login_page")
def Supp_Home(request):
    if request.user.user_type == 'supplier':
        user = request.user
        context = get_supplier_dashboard_data(request,user)
        return render(request,'Home.html',context)
    else:
        messages.error(request, "This user does not exist or is not a supplier.")
        return render(request,"Login.html")

@login_required(login_url="Login_page")
def earning(request):
    user = request.user
    supplier_profile = getattr(user, 'supplier', None)

    if not supplier_profile:
        return render(request, 'Earning.html', {
            'weekly_earnings': [],
            'total_earnings': 0,
            'is_available': False
        })

    driver = DriverDetail.objects.filter(user=supplier_profile).first()
    if not driver:
        return render(request, 'Earning.html', {
            'weekly_earnings': [],
            'total_earnings': 0,
            'is_available': supplier_profile.is_available
        })

    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(7)][::-1]

    weekly_earnings = []
    total_earnings = 0

    for day in last_7_days:
        daily_orders = OrderDetail.objects.filter(
            driver=driver,
            order_status='Delivered',
            order_date__date=day
        )

        total = daily_orders.aggregate(total=Sum('price'))['total'] or 0
        count = daily_orders.count()
        weekly_earnings.append({
            'date': day,
            'amount': total,
            'orders_count': count
        })
        total_earnings += total

    return render(request, 'Earning.html', {
        'weekly_earnings': weekly_earnings,
        'total_earnings': total_earnings,
        'is_available': supplier_profile.is_available
    })

@login_required(login_url="Login_page")
def order_request_view(request):
    supplier = getattr(request.user, 'supplier', None)
    if not supplier or not supplier.is_available:
        return render(request, "Order.html", {'orders': [], 'view_type': 'list'})

    driver_location = LocationDetail.objects.filter(user=request.user).last()
    if not driver_location:
        return render(request, "Order.html", {'orders': [], 'view_type': 'list'})

    all_orders = OrderDetail.objects.filter(order_status='Pending').select_related('location')
    nearby_orders = []

    for order in all_orders:
        dist = geodesic(
            (driver_location.latitude, driver_location.longitude),
            (order.location.latitude, order.location.longitude)
        ).km
        if dist <= 1.0:
            nearby_orders.append(order)

    return render(request, "Order.html", {'orders': nearby_orders, 'view_type': 'list'})

def order_detail(request, order_id):
    try:
        supplier = request.user.supplier
    except SupplierProfile.DoesNotExist:
        messages.error(request, "You are not a registered supplier.")
        return redirect('Home')

    order = get_object_or_404(OrderDetail, id=order_id, order_status='Pending')

    all_orders = OrderDetail.objects.filter(order_status='Pending').select_related('location')

    if request.method == "POST":
        action = request.POST.get('action')
        if action == 'accept':
            order.order_status = 'Accepted'
            order.driver = supplier
            order.save()
            Notification.objects.create(
                recipient=order.user,
                sender=request.user,
                message=f"Your order #{order.id} has been accepted by {request.user.first_name}",
                notification_type='order_accepted',
                order_id=order.id
            )
            messages.success(request, "Order accepted successfully!")
            return redirect('order_list')

        elif action == 'reject':
            order.order_status = 'Rejected'
            order.save()
            messages.info(request, "Order rejected.")
            return redirect('Home')

    return render(request, 'Order.html', {
    'orders': [order],
    'order': order, 
    'all_orders': all_orders,
    'view_type': 'detail'
})
@login_required(login_url="Login_page")
def order_list(request):
    driver = None

    if request.user.is_authenticated:
        try:
            supplier_profile = request.user.supplier
            driver = DriverDetail.objects.filter(user=supplier_profile).first()
        except Exception:
            driver = None

    orders = OrderDetail.objects.none()

    if driver:
        if request.method == 'POST':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('supplier_update_order_status')

            try:
                order = OrderDetail.objects.get(id=order_id, driver=driver)
                if new_status == 'cancel':
                    order.order_status = 'Cancelled'
                elif new_status == 'on_way':
                    order.order_status = 'On the Way'
                elif new_status == 'complete':
                    order.order_status = 'Completed'
                order.save()
                messages.success(request, f"Order updated to '{order.order_status}'.")
            except OrderDetail.DoesNotExist:
                messages.error(request, "Order not found or unauthorized.")

            return redirect('order_list')  
        
        if request.method == 'GET':
            orders = OrderDetail.objects.filter(
                order_status='Accepted',
                driver=driver
            ).select_related('user', 'location', 'driver', 'tanker')

    context = {'orders': orders if driver else None}
    return render(request, 'Order_List.html', context)

@login_required(login_url="Login_page")
def notification(request):
    if request.user.user_type == 'supplier':
        user = request.user
        dashboard_context = get_supplier_dashboard_data(request,user)
        notifications = Notification.objects.filter(customer=request.user).order_by('-timestamp')
        context = {
            **dashboard_context,
            'notifications': notifications
        }
        return render(request,'Notification.html',context)

    else:
        messages.error(request, "This user does not exist or is not a supplier.")
        return render(request,"Login.html")
    
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