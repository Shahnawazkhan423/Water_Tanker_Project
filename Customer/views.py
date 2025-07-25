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
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

@login_required(login_url="login")
def home(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'customer') and user.user_type == 'customer':
        return render(request,'home.html')
    else:
        return redirect('login')

@csrf_exempt
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

                    OrderDetail.objects.create(
                        user=user,
                        tanker=tanker,
                        location=location,
                        quantity=capacity,
                        price=total_price,
                        order_status='Pending'
                    )

                    messages.success(request, f"✅ Booking successful! Price: ₹{total_price:.2f} for {capacity} liters")
                    return redirect('booking')

            except Exception as e:
                messages.error(request, f"❌ Something went wrong: {str(e)}")
        else:
            messages.error(request, "⚠️ Please correct the errors in the form.")
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
    orders = OrderDetail.objects.filter(user=request.user,order_status='Accepted')
    return render(request, 'driver_detail.html', {'orders':orders})

@login_required(login_url="login")
def profile(request):
    user =request.user
    if request.user.is_authenticated and hasattr(user, 'user_type') and user.user_type == 'customer':
        return render(request, 'profile.html', {'user': request.user})
    else:
        return redirect('login')

@login_required
def update_profile_image(request):
    if request.method == 'POST' and 'profile_image' in request.FILES:
        profile_image = request.FILES['profile_image']
        user = request.user
        user.profile_image = profile_image
        user.save()
    return redirect('profile')  
   
@login_required(login_url="login")
def notification_view(request):
    try:
        supplier_profile = request.user.supplier 
    except Exception:
        return render(request, 'notification.html', {'notifications': []})

    notifications = Notification.objects.filter(supplier=supplier_profile).order_by('-timestamp')
    return render(request, 'notification.html', {'notifications': notifications})

def cancel_order(request, order_id):
    order = get_object_or_404(OrderDetail, id=order_id, user=request.user)

    if order.order_status in ['On the Way', 'Delivered']:
        messages.warning(request, "This order cannot be cancelled.")
        return redirect("driver_detail", order_id=order.id)  

    if request.method == "POST":
        order.order_status = 'Canceled'
        order.save()

        driver_detail = order.driver  
        supplier = driver_detail.user.supplier  

        Notification.objects.create(
            customer=request.user,
            supplier=supplier,  
            message=f"Order ID {order.id} has been cancelled by the customer."
        )
        messages.success(request, "Order has been cancelled successfully.")
        context = {
            'order': order,
            'driver': supplier
        }
    return render(request, "driver_detail.html", context)

    
@login_required
def delete_notification(request, id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=id, supplier__user=request.user)
        notification.delete()
