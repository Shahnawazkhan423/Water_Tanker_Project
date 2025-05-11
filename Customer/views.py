from django.shortcuts import render,redirect,get_object_or_404
from Supplier.models import *
from Customer.models import *
from Customer.forms import UserDetailForm, TankerDetailForm,LocationDetailForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.gis.measure import D
from django.contrib.gis.geos import Point
from django.db import transaction
from notifications.models import Notification
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
            return redirect('login')
    else:
        user_form = UserDetailForm()
        location_form = LocationDetailForm()

    return render(request, 'register.html', {'user_form': user_form, 'location_form': location_form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('id_passwords')
        user = authenticate(request, email=email, password=password)
        if user is not None and isinstance(user, CustomUser):
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        return render(request,'home.html')
    else:
        return redirect('login')

@login_required(login_url="login")
def booking(request):
    if request.method == "POST":
        user_form = UserDetailForm(request.POST)
        tanker_form = TankerDetailForm(request.POST)
        location_form = LocationDetailForm(request.POST)

        if user_form.is_valid() and tanker_form.is_valid() and location_form.is_valid():
            try:
                with transaction.atomic():
                    location = location_form.save(commit=False)
                    location.coordinates = Point(0, 0)  # Replace with actual geocoding
                    location.save()
                    
                    # Get all available suppliers within 1km radius
                    supplier_locations = LocationDetail.objects.filter(
                        coordinates__distance_lte=(location.coordinates, D(km=1))
                    )
                    # Get available tankers from available suppliers
                    available_tankers = TankerDetail.objects.filter(
                        available=True,
                        driver__user__is_available=True,  # Only available suppliers
                        driver__user__location__in=supplier_locations
                    ).select_related('driver__user')
                    
                    if not available_tankers:
                        messages.error(request, "No available tankers in your area at the moment.")
                        return redirect('booking')
                    
                    # Create pending order requests for all available tankers
                    orders = []
                    for tanker in available_tankers:
                        order = OrderDetail(
                            user=request.user,
                            driver=tanker.driver,
                            tanker=tanker,
                            location=location,
                            order_status='Pending'
                        )
                        orders.append(order)
                    
                    OrderDetail.objects.bulk_create(orders)
                    
                    # Create notifications for suppliers
                    for tanker in available_tankers:
                        Notification.objects.create(
                            recipient=tanker.driver.user,
                            sender=request.user,
                            message=f"New booking request from {request.user.first_name}",
                            notification_type='new_order',
                            order_id=orders[0].id  # Assuming first order ID
                        )
                    
                    messages.success(request, "Your request has been sent to nearby suppliers!")
                    return redirect('home')
                
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        user_form = UserDetailForm()
        tanker_form = TankerDetailForm()
        location_form = LocationDetailForm()

    return render(request, 'booking.html', {
        'user_form': user_form,
        'tanker_form': tanker_form,
        'location_form': location_form
    })

@login_required(login_url="login")
def driver_detail(request):
    if request.method=='GET':
        driver = DriverDetail.objects.select_related('user').first()
        status = OrderDetail.objects.select_related().first()

        context = {
            'driver_name': f"{driver.user.first_name} {driver.user.last_name}" if driver else 'N/A',
            'driver_number': driver.user.phone_number if driver else 'N/A',
            'order_date': status.delivery_date if status else 'N/A',
            'order_status': status.order_status if status else 'N/A',
            
        } 

    
    return render(request,'driver_detail.html',context)

@login_required(login_url="login")
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'user': request.user})
    else:
        return redirect('login')
    
@login_required(login_url="login")
def notification_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    return render(request, 'notification.html', {'notifications': notifications})

@login_required(login_url="login")
def mark_notification_read(request, notification_id):
    notification = Notification.objects.filter(
        id=notification_id, 
        recipient=request.user
    ).first()
    if notification:
        notification.is_read = True
        notification.save()
    return redirect('notification')
 

def customer_cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(TankerDetail, id=order_id, user=request.user)
        
        # Only allow cancellation if order isn't already completed/canceled
        if order.order_status not in ['Delivered', 'Canceled']:
            order.order_status = 'Canceled'
            order.save()
            
            # Create notification for supplier
            Notification.objects.create(
                recipient=order.driver.user,  # or the supplier user
                sender=request.user,
                message=f"Customer has canceled order #{order.id}",
                notification_type='order_canceled',
                order_id=order.id
            )
            
            messages.success(request, "Your order has been canceled.")
        else:
            messages.error(request, "This order cannot be canceled.")
    
    return redirect('driver_detail')  