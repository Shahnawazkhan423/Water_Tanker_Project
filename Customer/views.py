from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,'home.html')

def booking(request):
    return render(request,'booking.html')

def driver_detail(request):
    return render(request,'driver_detail.html')

def profile(request):
    return render(request,'profile.html')

def notification(request):
    return render(request,'notification.html')

