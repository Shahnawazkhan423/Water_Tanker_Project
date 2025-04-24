from django.shortcuts import render,redirect,get_object_or_404
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
        if user is not None:
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
    if request.method == "POST":
        user_form = UserDetailForm(request.POST)
        tanker_form = TankerDetailForm(request.POST)
        location_form = LocationDetailForm(request.POST)

        if user_form.is_valid() and tanker_form.is_valid() and location_form.is_valid():
            try:
                location = location_form.save()
                
                user = user_form.save(commit=False)
                user.location = location
                user.save()
                
                tanker = TankerDetail.objects.filter(available=True).first()
                if not tanker:
                    messages.error(request, "No available tankers at the moment.")
                    return redirect('booking')
                
                # Update tanker details from form
                tanker.capacity = tanker_form.cleaned_data['capacity']
                tanker.category = tanker_form.cleaned_data['category']
                tanker.save()
                
                # Create order
                from Customer.models import OrderDetail
                OrderDetail.objects.create(
                    user=user,
                    driver=tanker.driver,
                    tanker=tanker,
                    Location=location.address_line,
                    order_status='Pending'
                )
                
                messages.success(request, "Booking successful!")
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
def notification(request):
    return render(request,'notification.html')

