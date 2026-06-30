# 07 — Module Analysis

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [05-system-architecture.md](05-system-architecture.md) · [08-database-design.md](08-database-design.md) · [09-api-documentation.md](09-api-documentation.md)

---

## Module Map

```
┌─────────────────────────────────────────────────────────────┐
│                    UserManagement                           │
│  CustomUser · CustomUserManager · EmailBackend             │
│  CustomUserAdmin · role_selection view                     │
└──────────┬──────────────────────────────┬──────────────────┘
           │ AUTH_USER_MODEL              │
    ┌──────▼──────────┐         ┌─────────▼──────────────┐
    │   Customer App  │         │     Supplier App        │
    │                 │         │                         │
    │  CustomerProfile│         │  SupplierProfile        │
    │  LocationDetail │         │  LocationDetail (dup)   │
    │  OrderDetail    │◄────────│  DriverDetail           │
    │  Payment        │  FK     │  DriverAvailability     │
    │  Notification   │◄────────│  TankerDetail           │
    │                 │ Signal  │  WaterTankerDocument    │
    └─────────────────┘         └─────────────────────────┘
```

---

## Module 1: UserManagement

### Purpose
Central identity store. All three user types (`customer`, `supplier`, `admin`) share one Django user model. This app provides authentication infrastructure only — no business logic.

### `models.py`

**`CustomUserManager`**
- `create_user(email, password, **extra_fields)` — normalizes email, hashes password
- `create_superuser(email, password, **extra_fields)` — sets `is_staff=True`, `is_superuser=True`

**`CustomUser(AbstractBaseUser, PermissionsMixin)`**

| Field | Type | Notes |
|---|---|---|
| `email` | EmailField (unique) | USERNAME_FIELD — used for login |
| `first_name` | CharField(30) | Required |
| `last_name` | CharField(30) | Required |
| `phone_number` | CharField(15) | Optional |
| `user_type` | CharField choices | `customer` / `supplier` / `admin` |
| `profile_image` | ImageField | upload_to='media/', default set |
| `is_active` | BooleanField | Default True |
| `is_staff` | BooleanField | Default False |

### `backends.py` — EmailBackend
Replaces Django's default username-based authentication. Looks up user by email, verifies password. Registered as the primary `AUTHENTICATION_BACKENDS` entry.

### `views.py` — role_selection
The only view in this module. Renders the landing page (`base.html`) and handles POST to redirect to the appropriate login or register URL based on role selection.

### `admin.py` — CustomUserAdmin
Extends `UserAdmin` with:
- `list_display`: email, name, user_type, staff status, active
- `list_filter`: user_type, is_staff, is_active
- `search_fields`: email
- `fieldsets` for view/edit
- `add_fieldsets` for create

---

## Module 2: Customer App

### Purpose
Complete customer-facing domain. Handles the entire customer journey from registration through booking, order tracking, notifications, and profile management.

### `models.py`

**`LocationDetail`**
Delivery or registration address. Used by both `CustomerProfile` and `OrderDetail`.

| Field | Type | Notes |
|---|---|---|
| `address_line` | CharField(255) | |
| `street` | CharField(255) | |
| `landmark` | CharField(255) | Optional |
| `city` | CharField(255) | |
| `state` | CharField(255) | |
| `country` | CharField(255) | Default "India" |
| `pincode` | CharField(6) | Optional (but required in form) |
| `latitude` | FloatField | Optional — not used for matching |
| `longitude` | FloatField | Optional — not used for matching |

**`CustomerProfile`**
Extension of `CustomUser` for customer-specific data. One-to-one with `CustomUser`.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField(CustomUser) | related_name='customer' |
| `email` | EmailField (unique) | Auto-synced from `user.email` in `save()` |
| `forgot_password_token` | CharField(100) | UUID v4 token for password reset |
| `create_at` | DateTimeField | auto_now_add |
| `location` | ForeignKey(LocationDetail) | Registration address |

**`OrderDetail`**
The core transactional model. Links customer → driver → tanker → location.

| Field | Type | Notes |
|---|---|---|
| `user` | FK(CustomUser) | The customer who placed the order |
| `driver` | FK(DriverDetail) | Null until supplier accepts |
| `tanker` | FK(TankerDetail) | Set at booking time |
| `order_date` | DateTimeField | auto_now_add |
| `order_status` | CharField choices | Pending/Accepted/On the Way/Delivered/Canceled |
| `delivery_date` | DateTimeField | Nullable — never set in any view |
| `location` | FK(LocationDetail) | Delivery address |
| `quantity` | PositiveIntegerField | In liters (= tanker capacity) |
| `price` | DecimalField | Calculated at booking |

**`Payment`**
Payment record model — **never populated through any view**.

**`Notification`**
In-app messages between roles.

| Field | Type | Notes |
|---|---|---|
| `customer` | FK(CustomUser) | Recipient or initiator depending on `initiated_by` |
| `supplier` | FK(SupplierProfile) | |
| `message` | TextField | Human-readable notification text |
| `is_read` | BooleanField | Default False — **never set to True in any view** |
| `initiated_by` | CharField | `'customer'` or `'supplier'` |
| `timestamp` | DateTimeField | auto_now_add |

### `views.py` — 12 View Functions

| View | URL | Auth | Description |
|---|---|---|---|
| `register_view` | `/Customer/Register/` | Public | Creates CustomUser + CustomerProfile + LocationDetail |
| `login_view` | `/Customer/Login/` | Public | Email/password login with `user_type='customer'` guard |
| `logout_view` | `/Customer/Logout/` | Required | Clears session |
| `home` | `/Customer/` | Required | Customer dashboard |
| `booking` | `/Customer/Booking/` | Required | Booking form (GET pre-fills, POST creates order) |
| `driver_detail` | `/Customer/Driver_Detail/` | Required | Shows active (Accepted/On the Way) orders |
| `profile` | `/Customer/Profile/` | Required | Profile display |
| `update_profile_image` | `/Customer/update-profile-image/` | Required | Profile image upload |
| `notification` | `/Customer/Notifications/` | Required | Supplier-initiated notifications |
| `delete_notification` | `/Customer/notification/delete/<id>/` | Required | Delete a notification |
| `cancel_order` | `/Customer/order/<id>/cancel/` | None set | Cancel a pending/accepted order |
| `forgot_password` | `/Customer/forgot-password/` | Public | Request password reset |
| `reset_password` | `/Customer/reset-password/<token>/` | Public | Set new password via token |

### `forms.py`

**`UserDetailForm(ModelForm → CustomUser)`**
Fields: first_name, last_name, phone_number, email, password, profile_image.
Validations: Gmail-only email regex, 10-digit phone, letters-only name. Auto-sets `user_type='customer'` in `save()`.

**`BookingUserForm(ModelForm → CustomUser)`**
Fields: first_name, last_name, phone_number. Updates existing user's data at booking time.

**`TankerDetailForm(ModelForm → TankerDetail)`**
Fields: capacity, category. Dynamically injects price into capacity labels.

**`LocationDetailForm(ModelForm → LocationDetail [Customer])`**
Fields: address_line, street, landmark, city, state, pincode.

### `signals.py` + `receivers.py`
- `order_canceled_by_customer` — Signal fires when customer cancels an order
- Receiver `create_cancel_notification_for_supplier()` — creates a `Notification` record for the supplier

**Bug:** Receiver references `customer_user.name` which doesn't exist on `CustomUser` (should be `customer_user.first_name`).

### `tasks.py`
- `send_email_task(to, subject, message)` — async email via `send_mail()`
- `send_mail_every_day()` — bulk email to all users at 19:00 IST (**bug: only last user receives email**)

### `helper.py`
- `send_forgot_password_mail(request, email, token)` — synchronous password reset email
- **Bug:** Reset URL hardcoded to `http://127.0.0.1:8000`

### `utils.py`
- `haversine_distance(lat1, lon1, lat2, lon2)` — **Defined but never called in any view**

### `templatetags/custom_filters.py`
- `get_item(dictionary, key)` — Template filter to access dict by variable key
- `add_error_class(field)` — Adds `is-invalid` CSS class to form fields with errors

---

## Module 3: Supplier App

### Purpose
Complete supplier-facing domain. Handles supplier registration, tanker document management, availability, order management, earnings, and notifications.

### `models.py`

**`LocationDetail`** (duplicate of Customer's — same fields, different table)

**`SupplierProfile`**
One-to-one with `CustomUser` for supplier-specific data.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField(CustomUser) | related_name='supplier' |
| `email` | EmailField (unique) | Auto-synced from `user.email` |
| `is_available` | BooleanField | Default False — toggled by view |
| `created_at` | DateTimeField | auto_now_add |
| `location` | FK(LocationDetail) | Supplier's operating location |

**`DriverAvailability`**
Time-windowed availability log. Created each time supplier goes available.

| Field | Type | Notes |
|---|---|---|
| `user` | FK(CustomUser) | related_name='availabilities' |
| `availability_date` | DateField | |
| `start_time` | TimeField | When duty started |
| `end_time` | TimeField | Nullable — filled when going unavailable |
| `status` | CharField | `available` / `unavailable` |
| `notes` | CharField | Optional |

**`DriverDetail`**
Connects a user to their current availability record.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOneField(CustomUser) | |
| `availability` | FK(DriverAvailability) | related_name='supplier' |

**`WaterTankerDocument`**
Document set uploaded by supplier. Admin approves/rejects.

| Field | Type | Notes |
|---|---|---|
| `water_tanker_name` | CharField(100) | Name identifier |
| `is_approved` | CharField | `Pending` / `Approved` / `Rejected` |
| `profile_photo` | ImageField | upload_to='tanker/profile/' |
| `driving_license` | FileField | upload_to='tanker/license/' |
| `aadhar_card` | FileField | upload_to='tanker/aadhar/' |
| `pan_card` | FileField | upload_to='tanker/pan/' |
| `registration_cert` | FileField | upload_to='tanker/rc/' |
| `vehicle_insurance` | FileField | upload_to='tanker/insurance/' |
| `vehicle_permit` | FileField | upload_to='tanker/permit/' |
| `upload_date` | DateTimeField | auto_now_add |

**`TankerDetail`**
A specific tanker unit assigned to a driver.

| Field | Type | Notes |
|---|---|---|
| `driver` | FK(DriverDetail) | Nullable |
| `document` | FK(WaterTankerDocument) | Nullable |
| `capacity` | PositiveIntegerField | Choices: 1000/2000/5000/10000 |
| `category` | CharField | DRINKING/NON_DRINKING/BOTH |
| `available` | BooleanField | Default True |

**Computed properties:**
- `price_per_liter` — returns tier-based rate (0.15/0.12/0.10/0.08)
- `calculate_price()` — capacity × price_per_liter

### `views.py` — 14 View Functions

| View | URL | Auth | Description |
|---|---|---|---|
| `register_view` | `/Supplier/Registers/` | Public | Full registration + auto-creates driver records |
| `tanker_detail_view` | `/Supplier/Tanker_Detail/` | Required | Document + tanker upload |
| `login_view` | `/Supplier/Login/` | Public | Login — **missing role guard** |
| `logout_view` | `/Supplier/Logout/` | Public | Logout + render login template |
| `toggle_availability` | `/Supplier/toggle-availability/` | Required | JSON endpoint — toggle on/off |
| `Supp_Home` | `/Supplier/Home_Page/` | Required | Main dashboard |
| `get_supplier_dashboard_data` | (internal helper) | — | Returns dict with dashboard stats |
| `earning` | `/Supplier/Earning/` | Required | 7-day earnings breakdown |
| `order_list` | `/Supplier/Order-List` | Required | Pending/accepted/on-the-way orders |
| `update_order_status` | `/Supplier/orders/update-status/` | Required | Accept/cancel/update order |
| `notifications` | `/Supplier/Notifications/` | Required | Customer-initiated notifications |
| `delete_notification` | `/Supplier/supplier/notification/delete/<id>/` | None set | Delete notification |
| `profile` | `/Supplier/Profile/` | Required | Full profile view |
| `update_profile_image` | `/Supplier/Profile/Profile_Image/` | Required | Profile image upload |

### `signals.py` + `receivers.py`
4 signals, 4 receivers — one per order state change originating from supplier:

| Signal | Receiver | Message |
|---|---|---|
| `order_accepted_by_supplier` | `create_accepted_notification_for_customer` | "Your Order Has Been Accepted By..." |
| `order_on_the_way_by_supplier` | `create_on_the_away_notification_for_customer` | "Your Order is on the Way!..." |
| `order_delievery_by_supplier` | `create_delivery_notification_for_customer` | "Your Order Has Been Delivered..." |
| `order_canceled_by_supplier` | `create_canceled_notification_for_customer` | "Your Order Has Been Cancel..." |

**Note:** `order_delievery_by_supplier` — "delievery" is a typo in the signal name (should be "delivery").

### `utils.py`
- `haversine_distance()` — same as Customer's (duplicate)
- `human_readable_joined_date(joined_date)` — converts datetime to "X days/months/years ago" string using `relativedelta`

---

## Module 4: Custom Middleware

### `Water_Tanker_Project/middleware/session_override.py`

**`MultiAppSessionMiddleware`**

Intercepts every request before the view runs:
1. Checks URL path prefix (`/Supplier/` vs `/Customer/`)
2. Selects appropriate session cookie name and backend engine
3. Wraps session loading in `SimpleLazyObject` (lazy — only loaded if needed)
4. After response: if session was modified, saves it and sets cookie

**Note:** The middleware sets cookie `max_age=86400` (24h) but `SESSION_COOKIE_AGE=3600` (1h) is also set — these are inconsistent.

---

## Module 5: Celery Configuration

### `Water_Tanker_Project/celery.py`

```python
app = Celery('Water_Tanker_Project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Beat Schedule (Bug):**
```python
app.conf.beat_schedule = {'send_mail_every_day': {'task': 'Customer.tasks.send_mail_every_day', ...}}
app.conf.beat_schedule = {'send_mail_every_day': {'task': 'Supplier.tasks.send_mail_every_day', ...}}
# Second assignment overwrites the first — Customer task never runs via Beat
```

---

## Shared Utilities vs Duplicated Code

| Utility | Customer | Supplier | Should Be |
|---|---|---|---|
| `haversine_distance()` | `Customer/utils.py` | `Supplier/utils.py` | Shared utility |
| `send_email_task` | `Customer/tasks.py` | `Supplier/tasks.py` | Single shared task |
| `send_mail_every_day` | `Customer/tasks.py` | `Supplier/tasks.py` | Single shared task |
| `LocationDetail` model | `Customer/models.py` | `Supplier/models.py` | Shared model in UserManagement or new shared app |
| Registration form structure | `Customer/forms.py` | `Supplier/forms.py` | Base form class |
