from django.shortcuts import render

# Create your views here.
def Supp_Home(request):
    return render(request,'Home.html')

def earning(request):
    return render(request,'Earning.html')

def order(request):
    return render(request,'Order.html')

def order_list(request):
    return render(request,'Order_List.html')

def notification(request):
    return render(request,'Notification.html')

def profile(request):
    return render(request,'Profile.html')