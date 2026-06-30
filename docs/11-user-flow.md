# 11 — User Flow

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [02-business-requirements.md](02-business-requirements.md) · [09-api-documentation.md](09-api-documentation.md) · [12-data-flow.md](12-data-flow.md)

---

## Landing Page Flow

```
User visits: http://example.com/
  │
  ▼
UserManagement.views.role_selection
  │
  └── Renders: UserManagement/templates/base.html (extends _base.html)
      ├── Shows: "WaterTanker" brand + hero section
      ├── Two role cards: Customer / Supplier-Driver
      └── Direct links: Customer Login | Supplier Login (in nav)

POST (if form-based selection):
  user_role = 'customer' + user_role (register) → redirect 'register'
  user_role = 'customer' + user_role_login      → redirect 'login'
  user_role = 'supplier' + user_role (register) → redirect 'Register_page'
  user_role = 'supplier' + user_role_login      → redirect 'Login_page'
```

---

## Customer User Flow

### 1. Registration

```
GET /Customer/Register/
  └── Renders: Customer/templates/register.html
      ├── UserDetailForm (name, phone, email, password, profile image)
      └── LocationDetailForm (address, street, landmark, city, state, pincode)

POST /Customer/Register/
  ├── Validate both forms
  ├── Check email uniqueness in CustomerProfile
  ├── Save: LocationDetail → CustomUser (type=customer) → CustomerProfile
  ├── Queue email: send_email_task.delay(email, "Registration Successful", message)
  └── Redirect → /Customer/Login/
```

### 2. Login

```
GET /Customer/Login/
  └── Renders: Customer/templates/login.html

POST /Customer/Login/
  ├── authenticate(email, password)
  ├── Check: user.user_type == 'customer'
  ├── login(request, user) → set customer_sessionid cookie
  └── Redirect → /Customer/ (home)
```

### 3. Home Dashboard

```
GET /Customer/
  ├── Guard: @login_required + user_type == 'customer'
  └── Renders: Customer/templates/home.html
      └── Navigation: Booking | Driver Detail | Notifications | Profile | Logout
```

### 4. Booking

```
GET /Customer/Booking/
  └── Renders: Customer/templates/booking.html
      ├── BookingUserForm (pre-filled: name, phone from CustomUser)
      ├── TankerDetailForm (capacity with price labels, category)
      └── LocationDetailForm (pre-filled from CustomerProfile.location if exists)

POST /Customer/Booking/
  ├── Validate all 3 forms
  ├── atomic transaction:
  │   ├── user_form.save() → update CustomUser (name/phone)
  │   ├── TankerDetail.save(commit=False) → new phantom tanker record
  │   ├── Calculate price from capacity pricing dict
  │   ├── LocationDetail.save() → new delivery address record
  │   └── OrderDetail.objects.create(
  │         user=user, tanker=tanker, location=location,
  │         quantity=capacity, price=total_price, status='Pending'
  │       )
  └── Success: messages.success + redirect back to /Customer/Booking/
```

### 5. Order Tracking

```
GET /Customer/Driver_Detail/
  └── Renders: Customer/templates/driver_detail.html
      └── Orders filtered by: user=request.user AND
          (status='Accepted' OR status='On The Way')
          (Pending, Delivered, Canceled orders NOT shown here)
```

### 6. Cancel Order

```
GET /Customer/order/<id>/cancel/
  ├── Get order (404 if not found or not user's)
  ├── Check: status NOT in ['On the Way', 'Delivered']
  └── Renders confirmation UI in driver_detail.html

POST /Customer/order/<id>/cancel/
  ├── Set order.order_status = 'Canceled'
  ├── Save order
  ├── Get driver → supplier via order.driver.user.supplier
  └── Fire signal: order_canceled_by_customer
        └── Receiver creates Notification for supplier
```

### 7. Notifications

```
GET /Customer/Notifications/
  └── Renders: Customer/templates/notification.html
      └── Notification.objects.filter(
            customer=user,
            initiated_by='supplier'  ← only supplier-initiated messages
          ).order_by('-timestamp')
```

### 8. Delete Notification

```
POST /Customer/notification/delete/<id>/
  ├── Get notification (404 if not found)
  ├── notification.delete()
  └── Redirect → /Customer/Notifications/
```

### 9. Forgot Password

```
GET /Customer/forgot-password/
  └── Renders: Customer/templates/forgot_password.html

POST /Customer/forgot-password/
  ├── Find CustomUser by email
  ├── Generate token = uuid.uuid4()
  ├── Save to CustomerProfile.forgot_password_token
  ├── Send email via send_forgot_password_mail()  ← synchronous
  └── Redirect → /Customer/forgot-password/ (with success message)

GET /Customer/reset-password/<token>/
  ├── Find CustomerProfile by token
  └── Renders: Customer/templates/reset_passwords.html

POST /Customer/reset-password/<token>/
  ├── Validate new_password == confirm_password
  ├── user.set_password(new_password)
  ├── profile.forgot_password_token = None  ← clear token
  └── Redirect → /Customer/Login/
```

### 10. Profile

```
GET /Customer/Profile/
  └── Renders: Customer/templates/profile.html
      └── Shows: user.first_name, last_name, email, phone, profile_image, user_type

POST /Customer/update-profile-image/
  ├── Get uploaded file from request.FILES['profile_image']
  ├── user.profile_image = profile_image
  ├── user.save()
  └── Redirect → /Customer/Profile/
```

### 11. Logout

```
GET /Customer/Logout/
  ├── logout(request) → clears session
  ├── messages.success("Logged out successfully.")
  └── Redirect → /Customer/Login/
```

---

## Supplier User Flow

### 1. Registration (Two-Step Process)

**Step 1 — Account Registration:**
```
GET /Supplier/Registers/
  └── Renders: Supplier/templates/Register.html
      ├── SupplierRegistrationForm (name, phone, email, password, profile image)
      └── SupplierLocationDetailForm (address, city, state, pincode)

POST /Supplier/Registers/
  ├── Check email uniqueness in SupplierProfile
  ├── Validate forms
  ├── Save: LocationDetail → CustomUser (type=supplier)
  ├── Create: SupplierProfile (is_available=False)
  ├── Create: DriverAvailability (status='unavailable')
  ├── Create: DriverDetail (linked to availability)
  ├── Set session['supplier_email'] = user.email
  ├── Authenticate + login → set supplier_sessionid cookie
  └── Redirect → /Supplier/Tanker_Detail/
```

**Step 2 — Tanker & Document Registration:**
```
GET /Supplier/Tanker_Detail/
  └── Renders: Supplier/templates/tanker_detail.html
      ├── WaterTankerForm (tanker name + 7 document file uploads)
      └── SupplierTankerDetailForm (capacity, category)

POST /Supplier/Tanker_Detail/
  ├── Validate both forms (files must be JPG/PNG)
  ├── Save WaterTankerDocument (is_approved='Pending')
  ├── Get SupplierProfile from session['supplier_email']
  ├── Get DriverDetail from that user
  ├── Create: TankerDetail (driver=driver, document=doc, capacity, category)
  ├── Queue email: send_email_task.delay(...)
  ├── Delete session['supplier_email']
  └── Redirect → /Supplier/Home_Page/
      └── Supplier sees message: "Wait 24 hours for document verification"
```

### 2. Login

```
GET /Supplier/Login/
  └── Renders: Supplier/templates/Login.html

POST /Supplier/Login/
  ├── authenticate(email, password)
  ├── Check: isinstance(user, CustomUser)  ← ⚠️ Missing role guard
  ├── login(request, user)
  └── Redirect → /Supplier/Home_Page/
```

### 3. Dashboard (Home)

```
GET /Supplier/Home_Page/
  ├── Guard: @login_required + user_type == 'supplier'
  └── Renders: Supplier/templates/Home.html
      ├── If is_available=True:
      │     pending_orders = OrderDetail.filter(
      │         status='Pending',
      │         location__pincode=supplier.location.pincode
      │     )
      ├── recent_orders = OrderDetail.filter(
      │     status='Accepted',
      │     driver=driver_detail
      │   ).first()
      └── Stats: orders_accept, orders_complete, total_revenue, is_available
```

### 4. Availability Toggle

```
POST /Supplier/toggle-availability/ (via JavaScript fetch())
  ├── Check: user.is_authenticated AND user.user_type == 'supplier'
  ├── Get DriverDetail → TankerDetail → WaterTankerDocument
  ├── Check: document.is_approved == 'Approved'
  ├── Toggle: SupplierProfile.is_available = NOT current
  │
  ├── If going AVAILABLE:
  │     Create DriverAvailability(status='available', start_time=now)
  │     Update DriverDetail.availability = new_record
  │     Update TankerDetail.available = True
  │
  └── If going UNAVAILABLE:
        Get last DriverAvailability(status='available')
        Set last.end_time = now, last.status = 'unavailable'
        Update TankerDetail.available = False
  
  Returns JSON → JS updates UI toggle state
```

### 5. Order Management

```
GET /Supplier/Order-List
  ├── Guard: @login_required
  └── Renders: Supplier/templates/Order_List.html
      ├── If is_available=True:
      │     pending_orders = filter(status='Pending', pincode=supplier_pincode)
      ├── accepted_orders = filter(status='Accepted', driver=driver_detail)
      └── ontheway_orders = filter(status='On the Way', driver=driver_detail)

POST /Supplier/orders/update-status/
  ├── order_id, action = request.POST
  │
  ├── action == 'accept':
  │     order.status = 'Accepted'
  │     order.driver = driver_detail
  │     order.save()
  │     Fire: order_accepted_by_supplier → customer notification
  │
  ├── action == 'cancel':
  │     order.status = 'Canceled'
  │     order.driver = driver_detail
  │     order.save()
  │     Fire: order_canceled_by_supplier → customer notification
  │
  └── action == 'update_status':
        status_map: Canceled/On the Way/Delivered
        order.status = mapped_status
        order.save()
        If 'On the Way': Fire order_on_the_way_by_supplier → customer notification
        If 'Delivered':  Fire order_delievery_by_supplier → customer notification
```

### 6. Earnings

```
GET /Supplier/Earning/
  └── Renders: Supplier/templates/Earning.html
      ├── Today's earnings (sum of delivered orders today)
      └── Last 7 days:
          For i in range(7):
            day = today - i days
            orders = Delivered orders for that driver on that day
            {time_range, amount, orders_count, order_times}
```

### 7. Notifications

```
GET /Supplier/Notifications/
  └── Renders: Supplier/templates/Notification.html
      └── Notification.objects.filter(
            supplier=user.supplier
          ).order_by('-timestamp')
          ← ALL notifications (not filtered by initiated_by, unlike Customer)
```

### 8. Profile

```
GET /Supplier/Profile/
  └── Renders: Supplier/templates/Profile.html
      ├── user: CustomUser details
      ├── driver: DriverDetail with availability
      ├── tanker_detail: first TankerDetail for this driver
      ├── document: WaterTankerDocument linked to tanker
      ├── tankers: all TankerDetail records for this driver
      ├── location: SupplierProfile.location
      ├── rating: "4.5" (hardcoded)
      ├── orders_completed: count of all Delivered orders
      └── joined_since: human_readable_joined_date(user.supplier.created_at)
```

---

## Admin User Flow

```
GET /admin/
  └── Django Admin login

After login:
  ├── View/search/filter CustomUser records
  ├── Edit user details, change is_active, is_staff
  └── Manage WaterTankerDocument records:
        Change is_approved: Pending → Approved / Rejected
        (This is how supplier document verification is done)
```

---

## Cross-Role Notification Flow

```
Customer books order
  │
  │ Order sits as 'Pending'
  │ (No notification sent — supplier just sees it in their list)
  │
  ▼
Supplier accepts order
  │
  │ Signal: order_accepted_by_supplier
  │         └── Notification created for customer
  ▼
Customer sees notification: "Your Order Has Been Accepted By [Supplier Name]"
  │
  ▼
Supplier marks "On the Way"
  │
  │ Signal: order_on_the_way_by_supplier
  │         └── Notification created for customer
  ▼
Customer sees notification: "Your Order is on the Way! [Supplier Name] has started..."
  │
  ▼
Supplier marks "Delivered"
  │
  │ Signal: order_delievery_by_supplier
  │         └── Notification created for customer
  ▼
Customer sees notification: "Your Order Has Been Delivered By [Supplier Name]"

ALTERNATIVELY:

Customer cancels order
  │
  │ Signal: order_canceled_by_customer
  │         └── Notification created for supplier
  ▼
Supplier sees notification: "Order ID [X] has been cancelled by customer [name]"

OR:

Supplier cancels pending order
  │
  │ Signal: order_canceled_by_supplier
  │         └── Notification created for customer
  ▼
Customer sees notification: "Your Order Has Been Cancel By [Supplier Name]"
```
