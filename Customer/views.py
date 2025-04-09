from django.shortcuts import render
from Supplier.models import *
from Customer.models import *
from Customer.forms import UserDetailForm, TankerDetailForm,LocationDetailForm
from django.contrib import messages



# Create your views here.
def home(request):
    return render(request,'home.html')

def booking(request):
    if request.method == "POST":
        user_form = UserDetailForm(request.POST)
        tanker_form = TankerDetailForm(request.POST)
        location_form = LocationDetailForm(request.POST)

        
        if user_form.is_valid() and tanker_form.is_valid() and location_form.is_valid():
            location = location_form.save(commit=True)
            user = user_form.save()
            user.location = location
          
            print("user save data in in first save")

            tanker = tanker_form.save(commit=False)
            print('save for tanker')
            tanker.user = user

            default_driver = DriverDetail.objects.first()
            print("default_driver is ", default_driver)
            tanker.driver = default_driver
            print('tanker driver is', tanker.driver)
            tanker.save()
            user.save()
            location.save()
            messages.success(request, "Form submitted successfully!")

        else:
            messages.error(request, "Please correct the errors in the form.")

        
    else:
        user_form = UserDetailForm()
        tanker_form = TankerDetailForm()
        location_form = LocationDetailForm()


    return render(request, 'booking.html', {'user_form': user_form, 'tanker_form': tanker_form,'location_form': location_form
})

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

def profile(request):
    if request.method =="GET":
        customer = UserDetail.objects.select_related().first()
        context = {
            'user_name':f"{customer.first_name} {customer.last_name}" if customer else 'N/A',
        }
    return render(request,'profile.html',context)

def notification(request):
    return render(request,'notification.html')

