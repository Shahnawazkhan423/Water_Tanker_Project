from django.shortcuts import render
from Supplier.models import*

# Create your views here.
def home(request):
    return render(request,'home.html')

def booking(request):
    return render(request,'booking.html')

def driver_detail(request):
    if request.method=='GET':
        driver_name = request.GET.get('name', 'N/A')
        phone = request.GET.get('phone', 'N/A')
        delivery_time = request.GET.get('date', 'N/A')
        status = request.GET.get('status', 'N/A')

        context = {
            'driver_name': driver_name,
            'phone': phone,
            'delivery_time': delivery_time,
            'status': status
        } 
    
    
    return render(request,'driver_detail.html',context)

def profile(request):
    return render(request,'profile.html')

def notification(request):
    return render(request,'notification.html')

