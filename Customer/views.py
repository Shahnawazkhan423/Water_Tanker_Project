from django.shortcuts import render,redirect,get_object_or_404
from Supplier.models import *
from Customer.models import *
from Customer.forms import UserDetailForm, TankerDetailForm,LocationDetailForm,BookingUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import transaction
from geopy.distance import geodesic
from django.db.models import Subquery

# Create your views here.
def register_view(request):
    if request.method == "POST":
        user_form = UserDetailForm(request.POST, request.FILES)
        location_form = LocationDetailForm(request.POST)
        
        if user_form.is_valid() and location_form.is_valid():
            location = location_form.save()

            user = user_form.save(commit=False)
            user.location = location
            user.password = make_password(user_form.cleaned_data['password'])
            user.save()

            messages.success(request, 'Registration successful.')
            CustomerProfile.objects.create(user=user, location=location)
            return redirect("login")  
        
    else:
        user_form = UserDetailForm()
        location_form = LocationDetailForm()

    return render(request, 'register.html', {
        'user_form': user_form,
        'location_form': location_form
    })
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('id_passwords')
        user = authenticate(request, email=email, password=password)
        print('customer ka authentication', user)
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

@login_required(login_url="login")
def home(request):
    if request.user.is_authenticated:
        return render(request,'home.html')
    else:
        return redirect('login')

@login_required(login_url="login")
def booking(request):
    pricing = {
        1000: 1000 * 0.15,
        2000: 2000 * 0.12,
        5000: 5000 * 0.10,
        10000: 10000 * 0.08,
    }

    if request.method == "POST":
        user_form = BookingUserForm(request.POST, instance=request.user)
        tanker_form = TankerDetailForm(request.POST)
        location_form = LocationDetailForm(request.POST)

        if user_form.is_valid() and tanker_form.is_valid() and location_form.is_valid():
            try:
                with transaction.atomic():
                    user = user_form.save()

                    tanker = tanker_form.save(commit=False)
                    tanker.user = user
                    tanker.save()

                    capacity = tanker.capacity
                    total_price = pricing.get(capacity, 500.00)

                    location = location_form.save(commit=False)
                    location.user = user
                    location.tanker = tanker
                    location.save()

                    order = OrderDetail.objects.create(
                        user=user,
                        tanker=tanker,
                        location=location,
                        quantity=capacity,
                        price=total_price,
                        order_status='Pending'
                    )

                    # Step 1: Notify available drivers in 1 km
                    user_coords = (location.latitude, location.longitude)
                    available_user_ids = SupplierProfile.objects.filter(is_available=True).values('user_id')

                    available_drivers = DriverDetail.objects.filter(user__in=Subquery(available_user_ids))
                    for driver in available_drivers:
                        driver_coords = (driver.latitude, driver.longitude)
                        distance = geodesic(user_coords, driver_coords).km

                        if distance <= 1.0:
                            Notification.objects.create(
                                recipient=driver.user,
                                sender=user,
                                message=f"New booking request within 1 km for {capacity} liters",
                                notification_type='booking_request',
                                order_id=order.id
                            )

                    messages.success(request, f"Booking successful! Price: ₹{total_price:.2f} for {capacity} liters")
                    return redirect('booking')

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            errors = []
            for form in [user_form, tanker_form, location_form]:
                for field, error in form.errors.items():
                    errors.append(f"{form.fields[field].label}: {error[0]}")
            messages.error(request, " ".join(errors))
    else:
        user_form = BookingUserForm(instance=request.user)
        tanker_form = TankerDetailForm()
        location_form = LocationDetailForm()

    return render(request, 'booking.html', {
        'user_form': user_form,
        'tanker_form': tanker_form,
        'location_form': location_form,
        'pricing': pricing,
    })
@login_required(login_url="login")
def driver_detail(request):
    # Get the latest order for the current customer
    order = OrderDetail.objects.filter(
        user=request.user
    ).exclude(order_status__in=['Canceled', 'Delivered']).order_by('-order_date').first()
    
    context = {
        'order': order,
        'driver': order.driver if order else None,
        'order_status': order.order_status if order else 'No orders',
        'order_date': order.delivery_date if order else 'N/A'
    }
    return render(request, 'driver_detail.html', context)

@login_required(login_url="login")
def profile(request):
    if request.user.is_authenticated:
        return render(request, 'profile.html', {'user': request.user})
    else:
        return redirect('login')
    
@login_required(login_url="login")
def notification_view(request):
    try:
        supplier_profile = request.user.supplier  # Correctly fetch SupplierProfile
    except Exception:
        messages.error(request, "Supplier profile not found.")
        return render(request, 'notification.html', {'notifications': []})

    notifications = Notification.objects.filter(supplier=supplier_profile).order_by('-timestamp')
    return render(request, 'notification.html', {'notifications': notifications})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(OrderDetail, id=order_id, user=request.user)

    if order.order_status in ['On the Way', 'Delivered']:
        messages.warning(request, "This order cannot be cancelled.")
        context ={
            "order_id":order.id
        }
        return render(request,"home.html",context)

    if request.method == "POST":
        order.order_status = 'Canceled'
        order.save()

        Notification.objects.create(
            customer=request.user,  
            supplier=order.driver,  
            message=f"Order ID {order.id} has been cancelled by the customer.",
            id=order.id
        )
        messages.success(request, "Order has been cancelled successfully.")
        return render(request,"driver_detail.html")
    
@login_required
def delete_notification(request, id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=id, supplier__user=request.user)
        notification.delete()
