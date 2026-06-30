# 12 — Data Flow

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [05-system-architecture.md](05-system-architecture.md) · [08-database-design.md](08-database-design.md) · [11-user-flow.md](11-user-flow.md)

---

## 1. Customer Registration Data Flow

```
Browser Input:
  first_name, last_name, phone, email, password, profile_image
  address_line, street, landmark, city, state, pincode

        │
        ▼ POST /Customer/Register/
        
View: register_view()
  │
  ├── Form Validation (UserDetailForm + LocationDetailForm)
  │     ├── Server: clean_email() → Gmail regex check
  │     ├── Server: clean_phone_number() → 10-digit check
  │     └── Server: clean_first/last_name() → letters-only check
  │
  ├── DB Read:  CustomerProfile.objects.filter(email=email).exists()
  │
  ├── DB Write 1: location = LocationDetailForm.save()
  │                → INSERT INTO customer_locationdetail
  │
  ├── DB Write 2: user = UserDetailForm.save(commit=False)
  │                user.user_type = 'customer'
  │                user.password = make_password(raw_password)
  │                user.save()
  │                → INSERT INTO usermanagement_customuser
  │
  ├── DB Write 3: CustomerProfile.objects.create(user=user, location=location)
  │                → INSERT INTO customer_customerprofile
  │                   (email auto-filled from user in save())
  │
  └── Async: send_email_task.delay(email, subject, message)
              → Redis Queue → Celery Worker → Gmail SMTP
  
Response: HTTP 302 → /Customer/Login/
```

---

## 2. Booking Data Flow

```
Browser Input:
  first_name, last_name, phone (update user)
  capacity, category (tanker choice)
  address_line, street, landmark, city, state, pincode (delivery address)

        │
        ▼ POST /Customer/Booking/
        
View: booking()
  │
  ├── DB Read:  CustomerProfile.objects.get(user=request.user)
  │              → Prefill location form from profile.location
  │
  ├── Form Validation:
  │     BookingUserForm + TankerDetailForm + LocationDetailForm
  │
  ├── atomic transaction:
  │     │
  │     ├── DB Write 1: user = BookingUserForm.save()
  │     │                → UPDATE usermanagement_customuser (name, phone)
  │     │
  │     ├── Price Calculation:
  │     │     pricing = {1000: 150, 2000: 240, 5000: 500, 10000: 800}
  │     │     total_price = pricing[capacity]
  │     │
  │     ├── DB Write 2: tanker = TankerDetailForm.save(commit=False)
  │     │                tanker.user = user   ← ⚠️ TankerDetail has no 'user' field
  │     │                tanker.save()
  │     │                → INSERT INTO supplier_tankerdetail
  │     │
  │     ├── DB Write 3: location = LocationDetailForm.save(commit=False)
  │     │                location.user = user   ← ⚠️ LocationDetail has no 'user' field
  │     │                location.save()
  │     │                → INSERT INTO customer_locationdetail
  │     │
  │     └── DB Write 4: OrderDetail.objects.create(
  │                        user=user,
  │                        tanker=tanker,
  │                        location=location,
  │                        quantity=capacity,
  │                        price=total_price,
  │                        order_status='Pending'
  │                      )
  │                      → INSERT INTO customer_orderdetail
  │                         driver=NULL (no driver yet)
  │
Response: HTTP 302 → /Customer/Booking/ (with success message)
```

---

## 3. Order Acceptance Data Flow

```
Browser Input (Supplier dashboard):
  order_id=<int>, action='accept'

        │
        ▼ POST /Supplier/orders/update-status/
        
View: update_order_status()
  │
  ├── DB Read 1: order = OrderDetail.objects.get(id=order_id)
  ├── DB Read 2: driver_detail = DriverDetail.objects.get(user=request.user)
  │
  ├── Validate: order.order_status == 'Pending'
  │
  ├── DB Write: order.order_status = 'Accepted'
  │              order.driver = driver_detail
  │              order.save()
  │              → UPDATE customer_orderdetail
  │                SET order_status='Accepted', driver_id=<id>
  │
  └── Signal Dispatch:
        order_accepted_by_supplier.send(
          sender=OrderDetail,
          order_instance=order,
          supplier_user=driver_detail.user.supplier,  ← DB Read 3: OneToOne lookup
          customer_instance=order.user
        )
          │
          └── Receiver: create_accepted_notification_for_customer()
                DB Write: Notification.objects.create(
                  supplier=supplier_user,
                  customer=customer_instance,
                  message="Your Order Has Been Accepted By [Name]",
                  initiated_by='supplier'
                )
                → INSERT INTO customer_notification

Response: HTTP 302 → /Supplier/Order-List
```

---

## 4. Notification Delivery Data Flow

```
Customer visits /Customer/Notifications/

        │
        ▼ GET /Customer/Notifications/
        
View: notification()
  │
  ├── DB Read: Notification.objects.filter(
  │              customer=request.user,
  │              initiated_by='supplier'     ← Only supplier-initiated
  │            ).order_by('-timestamp')
  │
  └── Renders notification.html
        Shows: message, timestamp for each notification

⚠️ Pull-based only — customer must refresh page to see new notifications
⚠️ is_read field never set — all notifications appear as if unread
```

---

## 5. Email Async Data Flow

```
View calls: send_email_task.delay(to, subject, message)
                │
                ▼
         Serialized to JSON
                │
                ▼
        Redis Broker (db=0)
         Queue: celery
                │
                ▼ (Celery worker picks up)
        send_email_task(to, subject, message)
                │
                ├── send_mail(subject, message, EMAIL_HOST_USER, [to])
                │         │
                │         ▼
                │   smtp.gmail.com:587 (TLS)
                │         │
                │         ▼
                │   Recipient's inbox
                │
                └── Result stored in Redis Backend (db=1)
```

---

## 6. Supplier Availability Toggle Data Flow

```
Supplier clicks toggle button on dashboard

        │
        ▼ JavaScript fetch() → POST /Supplier/toggle-availability/
        
View: toggle_availability()
  │
  ├── DB Read 1: DriverDetail.objects.get(user=supplier)
  ├── DB Read 2: TankerDetail.objects.get(driver=driver_detail)
  ├── DB Read 3: tanker_detail.document → WaterTankerDocument
  │
  ├── Check: document.is_approved == 'Approved'
  │
  ├── DB Read 4: supplier_profile = supplier.supplier (OneToOne)
  ├── new_status = NOT supplier_profile.is_available
  │
  ├── DB Write 1: supplier_profile.is_available = new_status
  │               supplier_profile.save()
  │
  ├── If going AVAILABLE:
  │     DB Write 2: DriverAvailability.objects.create(
  │                   user=supplier, status='available',
  │                   availability_date=now.date(),
  │                   start_time=now.time()
  │                 )
  │     DB Write 3: driver_detail.availability = new_availability
  │                 driver_detail.save()
  │     DB Write 4: tanker_detail.available = True
  │                 tanker_detail.save()
  │
  └── If going UNAVAILABLE:
        DB Read 5: last_log = DriverAvailability.filter(status='available').last()
        DB Write 2: last_log.end_time = now.time()
                    last_log.status = 'unavailable'
                    last_log.save()
        DB Write 3: tanker_detail.available = False
                    tanker_detail.save()

Response: JSON {status: 'success', is_available: bool, message: str}
  │
  └── JavaScript updates toggle UI without page reload
```

---

## 7. Celery Beat Scheduled Email Data Flow

```
Every day at 19:00 IST (Asia/Kolkata):

Celery Beat
  │
  ├── Fires: Supplier.tasks.send_mail_every_day   ← Customer task overwritten in config
  │
  └── Task execution:
        users = CustomUser.objects.all()       ← DB Read: all users
        for user in users:
          subject = f"Good Evening, {user.first_name}!"
          message = f"..."
          ← ⚠️ BUG: send_mail() is OUTSIDE the loop
        
        try:                                   ← Only executes for LAST user
          send_mail(subject, message, ..., [user.email])
        except ...:
          logger.error(...)

Actual behavior: Only the LAST user in the QuerySet receives the email.
```

---

## 8. Password Reset Data Flow

```
POST /Customer/forgot-password/
  │
  ├── DB Read: CustomUser.objects.filter(email=email).first()
  │
  ├── token = str(uuid.uuid4())
  │
  ├── DB Write: profile, _ = CustomerProfile.objects.get_or_create(user=user_obj)
  │              profile.forgot_password_token = token
  │              profile.save()
  │
  └── Synchronous email: send_forgot_password_mail(request, email, token)
        send_mail("Your Password Reset Link",
          "http://127.0.0.1:8000/Customer/reset-password/{token}/",  ← Hardcoded!
          settings.EMAIL_HOST_USER,
          [email]
        )

POST /Customer/reset-password/<token>/
  │
  ├── DB Read: CustomerProfile.objects.filter(forgot_password_token=token).first()
  ├── Validate: new_password == confirm_password
  │
  ├── DB Write 1: user_obj.set_password(new_password)
  │               user_obj.save()
  │
  ├── DB Write 2: profile_obj.forgot_password_token = None
  │               profile_obj.save()
  │
  └── Response: redirect to /Customer/Login/
```

---

## 9. Session Data Flow

```
Request arrives at /Customer/* or /Supplier/*

        │
        ▼ MultiAppSessionMiddleware.__call__()
        
  ├── Determine path prefix (/Customer/ or /Supplier/)
  ├── Select: session_key name + session engine module
  ├── Read cookie: request.COOKIES.get(session_key)
  └── request.session = LazyObject → engine.SessionStore(cookie_value)
                                      (loaded only when accessed)
  
        │ View runs, accesses request.session
        ▼
  Session Store loads:
    Customer: DB query → django_session table → session data (JSON)
    Supplier: Redis GET → session data (JSON)

        │ After view returns response
        ▼
  If session.modified:
    session.save() → DB/Redis
    response.set_cookie(key=session_key, value=session.session_key,
                        max_age=86400, httponly=True, samesite='Lax')
```

---

## Data Flow Summary: Queries per Page

| Page | Approximate DB Queries |
|---|---|
| Customer Home | 1 (user session) |
| Customer Booking (GET) | 2 (session + CustomerProfile) |
| Customer Booking (POST) | 4 writes + 1 read (atomic) |
| Customer Driver Detail | 2 (session + OrderDetail filter) |
| Customer Notifications | 2 (session + Notification filter) |
| Supplier Dashboard | 5-7 (session, DriverDetail, OrderDetail ×3, SupplierProfile) |
| Supplier Order List | 4-5 (session, DriverDetail, pending, accepted, on-the-way queries) |
| Supplier Earnings | 8+ (session, DriverDetail, 7× daily aggregation queries) |
| Supplier Profile | 5 (session, DriverDetail, TankerDetail, WaterTankerDocument, SupplierProfile) |

**No caching** is applied to any of these pages. Every page load hits the database.
