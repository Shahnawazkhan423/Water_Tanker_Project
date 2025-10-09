from django.shortcuts import render,redirect,get_object_or_404
from Supplier.models import *
from Customer.models import Notification,OrderDetail
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
from datetime import time
from django.utils.timezone import now
from .utils import human_readable_joined_date
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def register_view(request):
    if request.method == "POST":
        user_form = SupplierRegistrationForm(request.POST, request.FILES)
        location_form = SupplierLocationDetailForm(request.POST)

        email = request.POST.get("email")  # Directly fetch from POST
        if email and SupplierProfile.objects.filter(email=email).exists():
            messages.error(request, "Email ID already exists.")
            return redirect("Register_page")

        if user_form.is_valid() and location_form.is_valid():
            location = location_form.save()
            user = user_form.save(commit=False)
            user.location = location
            user.password = make_password(user_form.cleaned_data['password'])
            user.save()

            SupplierProfile.objects.create(
                user=user,
                location=location,
                is_available=False
            )


            driver_availability = DriverAvailability.objects.create(
                user=user,  
                status="unavailable",
                availability_date=timezone.now(),
                start_time=timezone.now().time(), 
            )

            DriverDetail.objects.create(
                user=user,  
                availability=driver_availability
            )
            request.session['supplier_email'] = user.email
            request.session.set_expiry(3600)
            user = authenticate(request, email=user.email, password=user_form.cleaned_data['password'])
            if user is not None:
                login(request, user) 
            messages.success(request, 'Registration successful.')
            return redirect("tanker_detail")
    else:
        user_form = SupplierRegistrationForm()
        location_form = SupplierLocationDetailForm()

    return render(request, 'Register.html', {
        'user_form': user_form,
        'location_form': location_form
    })

@csrf_exempt
@login_required(login_url="Login_page")
def tanker_detail_view(request):
    if request.method == "POST":
        document_form = WaterTankerForm(request.POST, request.FILES)
        tanker_detail_form = SupplierTankerDetailForm(request.POST)
    
        if document_form.is_valid() and tanker_detail_form.is_valid():
            water_tanker_name = document_form.cleaned_data.get('water_tanker_name')
            document_instance = document_form.save(commit=False)
            document_instance.water_tanker_name = water_tanker_name
            document_instance.save()
            supplier_id = request.session.get('supplier_email')
            if not supplier_id:
                messages.error(request, "Session expired. Please register again.")
                return redirect('Register_page')
            supplier_profile = SupplierProfile.objects.filter(email=supplier_id).first()
            if not supplier_profile:
                messages.error(request, "Supplier profile not found.")
                return redirect("Register_page")

            custom_user = supplier_profile.user
            driver = DriverDetail.objects.filter(user=custom_user).first()
            if not driver:
                messages.error(request, "Driver details not found.")
                return redirect("Register_page")

            # Check if supplier is currently available
            availability_status = DriverAvailability.objects.filter(
                user=custom_user,
                status='available'
            ).order_by('-availability_date').exists()

            # Save TankerDetail entry
            TankerDetail.objects.create(
                driver=driver,
                document=document_instance,
                capacity=tanker_detail_form.cleaned_data['capacity'],
                category=tanker_detail_form.cleaned_data['category'],
                available=availability_status
            )
            messages.success(request,  "Tanker registration successful. Please wait 24 hours for document verification before starting duty.")
            del request.session['supplier_email']
            return redirect('Home')
        else:
            messages.error(request, 'Please correct the form errors.')
    else:
        document_form = WaterTankerForm()
        tanker_detail_form = SupplierTankerDetailForm()

    return render(request, "tanker_detail.html", {
        'document': document_form,
        'tanker_detail': tanker_detail_form
    })

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if user is not None and isinstance(user,CustomUser):
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, "Login.html")

@csrf_exempt
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return render(request, "Login.html")
        
def toggle_availability(request):
    if not request.user.is_authenticated or request.user.user_type != 'supplier':
        return JsonResponse({
            'status': 'error',
            'message': 'Unauthorized access. Only suppliers can perform this action.'
        })

    # ✅ Step 2: Check method
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method. Use POST.'
        })

    supplier = request.user

    try:
        driver_detail = DriverDetail.objects.get(user=supplier)

        tanker_detail = TankerDetail.objects.get(driver=driver_detail)

        document = tanker_detail.document
        if not document or document.is_approved != "Approved":
            return JsonResponse({
                'status': 'error',
                'message': 'Please upload and get your documents approved first before becoming available.'
            })

        supplier_profile = supplier.supplier  # OneToOneField relation
        new_status = not supplier_profile.is_available
        supplier_profile.is_available = new_status
        supplier_profile.save()

        if new_status:
            availability = DriverAvailability.objects.create(
                user=supplier,
                availability_date=timezone.now().date(),
                start_time=timezone.now().time(),
                status='available'
            )
            driver_detail.availability = availability
            driver_detail.save()

            tanker_detail.available = True
            tanker_detail.save()
        else:
            last_log = DriverAvailability.objects.filter(
                user=supplier,
                status='available'
            ).last()

            if last_log:
                last_log.end_time = timezone.now().time()
                last_log.status = 'unavailable'
                last_log.save()

            tanker_detail.available = False
            tanker_detail.save()

        return JsonResponse({
            'status': 'success',
            'is_available': new_status,
            'message': f"Availability set to {'Available' if new_status else 'Unavailable'}."
        })

    except DriverDetail.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Driver profile not found. Please complete your profile first.'
        })

    except TankerDetail.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Tanker details not found. Please register your tanker.'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Unexpected error occurred: {str(e)}"
        })
@csrf_exempt
@login_required(login_url="Login_page")
def get_supplier_dashboard_data(request):
    data = {
        'orders_accept': 0,
        'orders_complete': 0,
        'total_revenue': 0,
        'orders_today': [],
        'is_available': False,
    }
    user = request.user

    if user.user_type != 'supplier':
        return data
    
    supplier_profile = getattr(user, 'supplier', None)
    if not supplier_profile:
        return data
    data['is_available'] = request.user.supplier.is_available

    driver = DriverDetail.objects.filter(user=user).first()
    if not driver:
        return data

    last_24_hours = now() - timedelta(hours=24)

    orders_last_24h = OrderDetail.objects.filter(
        order_status='Delivered',
        driver=driver,
        order_date__gte=last_24_hours  
    )
    data['orders_today'] = orders_last_24h
    data['total_revenue'] = orders_last_24h.aggregate(total=Sum('price'))['total'] or 0
   
    data['orders_accept'] = OrderDetail.objects.filter(order_status='Accepted', driver=driver).count()
    data['orders_complete'] = OrderDetail.objects.filter(order_status='Delivered', driver=driver).count()
    return data

@csrf_exempt
@login_required(login_url="Login_page")
def Supp_Home(request):
    context = {}

    if request.user.is_authenticated and request.user.user_type == 'supplier':
        supplier = request.user.supplier
        driver_detail = DriverDetail.objects.get(user=request.user)
        if supplier.is_available:
            supplier_pincode = supplier.location.pincode

            latest_order = OrderDetail.objects.filter(
                order_status='Pending',
                location__pincode=supplier_pincode
            ).select_related('user', 'location', 'tanker') # fetch latest 5
    
            context['latest_order'] = latest_order
        recent_orders = OrderDetail.objects.filter(
            order_status='Accepted',
            driver=driver_detail
        ).select_related('user', 'location', 'driver', 'tanker').order_by('-order_date').first()
        context['recent_orders'] = recent_orders
        dashboard_data = get_supplier_dashboard_data(request)
        context.update(dashboard_data)

        return render(request, 'Home.html', context)

    else:
        messages.error(request, "This user does not exist or is not a supplier.")
        return render(request, "Login.html")
@login_required(login_url="Login_page")
@csrf_exempt
def earning(request):
    user = request.user
    supplier_profile = getattr(user, 'supplier', None)

    if not supplier_profile:
        return render(request, 'Earning.html', {
            'earnings_today': None,
            'last_7_earnings': [],
            'total_earnings': 0,
            'is_available': False
        })

    driver = DriverDetail.objects.filter(user=user).first()
    if not driver:
        return render(request, 'Earning.html', {
            'earnings_today': None,
            'last_7_earnings': [],
            'total_earnings': 0,
            'is_available': supplier_profile.is_available
        })
    now = timezone.localtime(timezone.now())
    today = now.date()  # e.g., 2025-08-12
    last_7_earnings = []
    total_earnings = 0
    earnings_today = None

    for i in range(7):
        day = today - timedelta(days=i)
        start_time = timezone.make_aware(datetime.combine(day, time.min))  # 00:00:00
        end_time = timezone.make_aware(datetime.combine(day, time.max))    # 23:59:59.999999


        orders = OrderDetail.objects.filter(
            driver=driver,
            order_status='Delivered',
            order_date__gte=start_time,
            order_date__lt=end_time
        )
        total = orders.aggregate(total=Sum('price'))['total'] or 0
        count = orders.count()
        order_list = orders.values_list('order_date', flat=True).order_by('-order_date')

        label = f"{start_time.strftime('%d %b, %H:%M')} - {end_time.strftime('%H:%M')}"
        last_7_earnings.append({
            'time_range': label,
            'amount': total,
            'orders_count': count,
            'order_times': [dt.strftime('%d %b, %I:%M %p') for dt in order_list]
        })
        total_earnings += total
        
        if i == 0:
            earnings_today = {
                'amount': total,
                'completed_orders': count,
                'total_orders': OrderDetail.objects.filter(
                    driver=driver,
                    order_date__gte=start_time,
                    order_date__lt=end_time
                ).count()
            }

    return render(request, 'Earning.html', {
        'earnings_today': earnings_today,
        'last_7_earnings': last_7_earnings,
        'total_earnings': total_earnings,
        'is_available': supplier_profile.is_available,
        'orders_accept': OrderDetail.objects.filter(order_status='Accepted', driver=driver).count(),
        'orders_complete': OrderDetail.objects.filter(order_status='Delivered', driver=driver).count(),
    })

@csrf_exempt
@login_required(login_url="Login_page")
def order_list(request, order_id=None):
    try:
        supplier = request.user.supplier  
        driver_detail = DriverDetail.objects.get(user=request.user)
    except SupplierProfile.DoesNotExist:
        messages.error(request, "You are not a registered supplier.")
        return redirect('Home')
    except DriverDetail.DoesNotExist:
        messages.error(request, "Driver profile not found. Please complete your driver profile.")
        return redirect('Home')

    pending_orders = []
    accepted_orders = OrderDetail.objects.filter(
        order_status='Accepted',
        driver=driver_detail
    ).select_related('user', 'location', 'driver', 'tanker')
    ontheway_orders = OrderDetail.objects.filter(
        order_status='On the Way',
        driver=driver_detail
    ).select_related('user', 'location', 'driver', 'tanker')

    if supplier.is_available:
        supplier_pincode = supplier.location.pincode
        pending_orders = OrderDetail.objects.filter(
            order_status='Pending',
            location__pincode=supplier_pincode
        ).select_related('user', 'location', 'tanker')
    elif order_id:
        messages.warning(request, "You must be on duty to view order details")
        return redirect('order_list')

    context = {
        'view_type': 'list',
        'pending_orders': pending_orders,
        'accepted_orders': accepted_orders,
        'ontheway_orders' :ontheway_orders,
        'is_available': supplier.is_available, 
    }

    return render(request, 'Order_List.html', context)

@login_required(login_url="Login_page")
def notifications(request):
    try:
        user = request.user.supplier
    except Exception:
        return render(request, 'Notification.html', {'notifications': []})
    notifications = Notification.objects.filter(supplier=user).order_by('-timestamp')
    print(notifications)
    context = get_supplier_dashboard_data(request)
    context['notifications'] = notifications  
    return render(request, 'Notification.html',context)


@login_required(login_url="Login_page")
def profile(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'supplier') and request.user.user_type == 'supplier':
        driver = DriverDetail.objects.select_related('user', 'availability').get(user=user)
        tanker_detail = TankerDetail.objects.select_related('document').filter(driver=driver).first()
        document = tanker_detail.document if tanker_detail else None
        supplier_profile = SupplierProfile.objects.select_related('location').get(user=user)
        joined_since = human_readable_joined_date(user.supplier.created_at)
        tankers = TankerDetail.objects.select_related('document').filter(driver=driver)
        
        orders_last_24h = OrderDetail.objects.filter(
            order_status='Delivered',
            driver=driver,
        )
        count = orders_last_24h.count()
        context = {
                'user': user,
                'driver': driver,
                'tanker_detail': tanker_detail,
                'document': document,
                'tankers': tankers,
                'location': supplier_profile.location,
                'rating': "4.5", 
                'orders_completed': count,
                'joined_since': joined_since  
        }
        
        return render(request, 'Profile.html', context)
    else:
        messages.error(request, "This user does not exist or is not a supplier.")
        return render(request,"Login.html")


@login_required(login_url="Login_page")
def update_order_status(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        
        if not order_id or not action:
            messages.error(request, "Invalid request parameters.")
            return redirect('Order_List')
        
        try:
            order = OrderDetail.objects.get(id=order_id)
            driver_detail = DriverDetail.objects.get(user=request.user)
        except OrderDetail.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('Order_List')
        except DriverDetail.DoesNotExist:

            messages.error(request, "Driver profile not found.")
            return redirect('Order_List')

        # Handle accept/cancel actions
        if action in ['accept', 'cancel']:
            if order.order_status != 'Pending':
                messages.warning(request, "Order already processed.")
                return redirect('Order_List')

            if action == 'accept':
                order.order_status = 'Accepted'
                order.driver = driver_detail
                notif_message = f"Your order has been accepted by { request.user.first_name }."
            else:  # cancel
                order.order_status = 'Canceled'
                notif_message = f"Your order has been canceled by {request.user.first_name}."
            
            order.save()
            
            # Create notification
            Notification.objects.create(
                customer=order.user,
                supplier=driver_detail.user.supplier,
                message=notif_message,
                initiated_by='supplier'
            )
            messages.success(request, f"Order {order.id} {action}ed.")
        
        elif action == 'update_status':
            status_update = request.POST.get('supplier_update_order_status')
            status_map = {
                'Canceled': 'Canceled',
                'On the Way': 'On the Way',
                'Delivered': 'Delivered'
            }

            if status_update in status_map:
                order.order_status = status_map[status_update]
                order.save()
                if status_update == 'On the Way':
                    Notification.objects.create(
                        customer=order.user,
                        supplier=driver_detail.user.supplier,
                        message=f"Your order is now on the way.",
                        initiated_by='supplier'
                    )
                    messages.success(request, f"Order status updated to {order.get_order_status_display()}")
                elif status_update == "Delivered":
                    Notification.objects.create(
                        customer=order.user,
                        supplier=driver_detail.user.supplier,
                        message=f"Your order has been successfully delivered.",
                        initiated_by='supplier'
                    )
                    messages.success(request, f"Order status updated to {order.get_order_status_display()}")
            else:
                messages.error(request, "Invalid status update request.")
        
        else:
            messages.error(request, "Invalid action.")
        
        # FIX: Redirect back to order list
        return redirect('Order_List')
    
def delete_notification(request, id):
    notif = get_object_or_404(Notification, id=id)
    notif.delete()
    return redirect('Notification')

@login_required
def update_profile_image(request):
    if request.method == 'POST' and 'profile_image' in request.FILES:
        profile_image = request.FILES['profile_image']
        user = request.user
        user.profile_image = profile_image
        user.save()
    return redirect('Profile')  