from django.shortcuts import render,redirect,get_object_or_404
from Customer.models import *
from Customer.forms import UserDetailForm, TankerDetailForm,LocationDetailForm,BookingUserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import transaction
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .helper import send_forgot_password_mail
import uuid 
from  .signals import order_canceled_by_customer
@csrf_exempt
def register_view(request):
    if request.method == "POST":
        user_form = UserDetailForm(request.POST, request.FILES)
        location_form = LocationDetailForm(request.POST)
        email = request.POST.get("email")
            # Check if email exists
        if CustomerProfile.objects.filter(email=email).exists():
                messages.error(request, "Email ID already exists.")
                print("Email ID already exists.")
                return redirect("register")  
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
        print("User---", user)

        if user is not None and getattr(user, 'user_type', None) == 'customer':
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
            messages.error(request, "⚠️ Please fill in all required fields correctly before submitting the form.")
    else:
        user_form = BookingUserForm(instance=request.user)
        tanker_form = TankerDetailForm()
        try:
            customer_profile = CustomerProfile.objects.get(user=request.user)
            location_instance = customer_profile.location
            location_form = LocationDetailForm(instance=location_instance)
        except CustomerProfile.DoesNotExist:
            location_form = LocationDetailForm()
    return render(request, 'booking.html', {
        'user_form': user_form,
        'tanker_form': tanker_form,
        'location_form': location_form,
        'pricing': pricing,
    })
@login_required(login_url="login")
def driver_detail(request):
    orders = OrderDetail.objects.filter(
        Q(user=request.user),
        Q(order_status='Accepted') | Q(order_status='On The Way')
    )
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
def notification(request):
    user = request.user

    if user.user_type != "customer":
        return render(request, 'notification.html', {'notifications': []})

    notifications = Notification.objects.filter(
        customer=user,
        initiated_by='supplier'
    ).order_by('-timestamp')
    context = {
        'notifications': notifications
    }
    return render(request, 'notification.html', context)
def cancel_order(request, order_id):
    order = get_object_or_404(OrderDetail, id=order_id, user=request.user)

    if order.order_status in ['On the Way', 'Delivered']:
        messages.warning(request, "This order cannot be cancelled.")
        return redirect("driver_detail")  

    if request.method == "POST":
        order.order_status = 'Canceled'
        order.save()

        driver_detail = order.driver  
        supplier = driver_detail.user.supplier  

        order_canceled_by_customer.send(
            sender=OrderDetail,              
            order_instance=order,             
            customer_user=request.user,       
            supplier_instance=supplier,       
        )
        print("detail:---",order_canceled_by_customer)
        messages.success(request, "Order has been cancelled successfully.")

    return render(request, "driver_detail.html")

    
@login_required
def delete_notification(request, id):
    if request.method == 'POST':
        notif = get_object_or_404(Notification, id=id)
        notif.delete()
        return redirect('notification')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        print("Email entered:", email)

        user_obj = CustomUser.objects.filter(email=email).first()
        if not user_obj:
            messages.error(request, "No user found with this email.")
            return redirect("forgot_password")

        # Generate and save token
        token = str(uuid.uuid4())
        profile, created = CustomerProfile.objects.get_or_create(user=user_obj)
        profile.forgot_password_token = token
        profile.save()

        if send_forgot_password_mail(request, user_obj.email, token):
            messages.success(request, "An email has been sent with password reset instructions.")
        else:
            messages.error(request, "We couldn't send the reset email. Please try again later.")

        return redirect("forgot_password")

    return render(request, "forgot_password.html")


def reset_password(request, token):
    profile_obj = CustomerProfile.objects.filter(forgot_password_token=token).first()
    if not profile_obj:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("forgot_password")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(f"/Customer/reset-password/{token}/")

        user_obj = profile_obj.user
        user_obj.set_password(new_password)
        user_obj.save()

        # Clear the token after reset
        profile_obj.forgot_password_token = None
        profile_obj.save()

        messages.success(request, "Password reset successfully. Please log in.")
        return redirect("login")

    return render(request, "reset_passwords.html", {'user_id': profile_obj.user.id})
