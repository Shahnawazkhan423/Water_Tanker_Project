# 09 — API Documentation

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [07-module-analysis.md](07-module-analysis.md) · [10-authentication.md](10-authentication.md) · [12-data-flow.md](12-data-flow.md)

---

## API Type

This application uses **server-rendered HTML** responses (Django MVT) for all views except one. There is **no REST API** for external clients.

The single JSON-returning endpoint is:

| Endpoint | Method | Returns |
|---|---|---|
| `/Supplier/toggle-availability/` | POST | JSON `{status, is_available, message}` |

**DRF is installed** (`djangorestframework==3.14.0`) but no ViewSets, Serializers, or Router configurations exist. It is currently unused.

---

## Root URLs

| URL | Method | View | Auth | Description |
|---|---|---|---|---|
| `/` | GET, POST | `UserManagement.views.role_selection` | Public | Landing page; POST redirects to role-appropriate login/register |
| `/admin/` | ALL | Django Admin | Staff only | Django admin panel |

---

## Customer Endpoints

Base prefix: `/Customer/`

| URL | Method | View | Auth Required | Description |
|---|---|---|---|---|
| `/Customer/Register/` | GET | `register_view` | No | Render registration form |
| `/Customer/Register/` | POST | `register_view` | No | Create account + CustomerProfile + send email |
| `/Customer/Login/` | GET | `login_view` | No | Render login form |
| `/Customer/Login/` | POST | `login_view` | No | Authenticate + set session (customer role check) |
| `/Customer/Logout/` | GET | `logout_view` | Yes (`@login_required`) | Clear session, redirect to login |
| `/Customer/` | GET | `home` | Yes | Customer dashboard/home page |
| `/Customer/Booking/` | GET | `booking` | Yes | Booking form (pre-filled from profile) |
| `/Customer/Booking/` | POST | `booking` | Yes | Submit booking → create OrderDetail |
| `/Customer/Driver_Detail/` | GET | `driver_detail` | Yes | Active orders (Accepted + On the Way) |
| `/Customer/Profile/` | GET | `profile` | Yes | User profile page |
| `/Customer/update-profile-image/` | POST | `update_profile_image` | Yes (`@login_required`) | Upload new profile image |
| `/Customer/Notifications/` | GET | `notification` | Yes | In-app notifications from supplier |
| `/Customer/notification/delete/<int:id>/` | POST | `delete_notification` | Yes (`@login_required`) | Delete a notification record |
| `/Customer/order/<int:order_id>/cancel/` | GET, POST | `cancel_order` | No (`@login_required` missing) | Cancel a pending/accepted order |
| `/Customer/forgot-password/` | GET | `forgot_password` | No | Render forgot password form |
| `/Customer/forgot-password/` | POST | `forgot_password` | No | Generate reset token + send email |
| `/Customer/reset-password/<token>/` | GET | `reset_password` | No | Render new password form |
| `/Customer/reset-password/<token>/` | POST | `reset_password` | No | Save new password + clear token |

---

## Supplier Endpoints

Base prefix: `/Supplier/`

| URL | Method | View | Auth Required | Description |
|---|---|---|---|---|
| `/Supplier/Registers/` | GET | `register_view` | No | Render supplier registration form |
| `/Supplier/Registers/` | POST | `register_view` | No | Create account + auto-create driver records |
| `/Supplier/Tanker_Detail/` | GET | `tanker_detail_view` | Yes (`@login_required`) | Render tanker + document upload form |
| `/Supplier/Tanker_Detail/` | POST | `tanker_detail_view` | Yes | Upload documents + create TankerDetail |
| `/Supplier/Login/` | GET | `login_view` | No | Render supplier login form |
| `/Supplier/Login/` | POST | `login_view` | No | Authenticate (⚠️ missing role guard) |
| `/Supplier/Logout/` | GET | `logout_view` | No | Clear session, render login page |
| `/Supplier/toggle-availability/` | POST | `toggle_availability` | Yes (manual check) | **JSON** — toggle supplier on/off duty |
| `/Supplier/Home_Page/` | GET | `Supp_Home` | Yes (`@login_required`) | Supplier dashboard |
| `/Supplier/Earning/` | GET | `earning` | Yes (`@login_required`) | 7-day earnings report |
| `/Supplier/Order-List` | GET | `order_list` | Yes (`@login_required`) | All orders (pending/accepted/on-the-way) |
| `/Supplier/orders/update-status/` | POST | `update_order_status` | Yes (`@login_required`) | Accept/cancel/update order status |
| `/Supplier/Notifications/` | GET | `notifications` | Yes (`@login_required`) | Customer-initiated notifications |
| `/Supplier/supplier/notification/delete/<int:id>/` | GET | `delete_notification` | No (missing) | Delete a notification |
| `/Supplier/Profile/` | GET | `profile` | Yes (`@login_required`) | Full supplier profile |
| `/Supplier/Profile/Profile_Image/` | POST | `update_profile_image` | Yes (`@login_required`) | Upload new profile image |

---

## JSON Endpoint Detail

### `POST /Supplier/toggle-availability/`

**Purpose:** Toggle supplier on/off duty. Called via JavaScript `fetch()` from the supplier dashboard.

**Authentication:** Manual check in view — requires `request.user.is_authenticated` and `user_type == 'supplier'`.

**Request:**
```
POST /Supplier/toggle-availability/
Content-Type: application/x-www-form-urlencoded
Cookie: supplier_sessionid=<session_key>
Body: csrfmiddlewaretoken=<token>
```
Note: `@csrf_exempt` is applied to this view, so CSRF token is not actually validated.

**Response (Success):**
```json
{
  "status": "success",
  "is_available": true,
  "message": "Availability set to Available."
}
```

**Response (Error cases):**
```json
{"status": "error", "message": "Unauthorized access. Only suppliers can perform this action."}
{"status": "error", "message": "Invalid request method. Use POST."}
{"status": "error", "message": "Please upload and get your documents approved first..."}
{"status": "error", "message": "Driver profile not found. Please complete your profile first."}
{"status": "error", "message": "Tanker details not found. Please register your tanker."}
{"status": "error", "message": "Unexpected error occurred: <detail>"}
```

**Side effects on success:**
- Toggles `SupplierProfile.is_available`
- Creates new `DriverAvailability` record (when going available)
- Updates last `DriverAvailability` record with `end_time` (when going unavailable)
- Updates `TankerDetail.available` to match

---

## POST Form Data Structures

### Customer Registration (`POST /Customer/Register/`)

```
first_name=<str>
last_name=<str>
phone_number=<10-digit, starts 6-9>
email=<gmail.com address>
password=<str>
profile_image=<file, optional>
address_line=<str, 5-100 chars, alphanumeric>
street=<str, 3-50 chars, letters only>
landmark=<str, optional>
city=<str, 2-50 chars, letters only>
state=<dropdown selection>
pincode=<6-digit number>
csrfmiddlewaretoken=<token>
```

### Booking (`POST /Customer/Booking/`)

```
first_name=<str>
last_name=<str>
phone_number=<str>
capacity=<1000|2000|5000|10000>
category=<DRINKING|NON_DRINKING|BOTH>
address_line=<str>
street=<str>
landmark=<str, optional>
city=<str>
state=<str>
pincode=<str>
csrfmiddlewaretoken=<token>
```

### Order Status Update (`POST /Supplier/orders/update-status/`)

```
order_id=<int>
action=<accept|cancel|update_status>
supplier_update_order_status=<Canceled|On the Way|Delivered>  (required if action=update_status)
csrfmiddlewaretoken=<token>
```

### Tanker Document Upload (`POST /Supplier/Tanker_Detail/`)

```
water_tanker_name=<str>
profile_photo=<image file, JPG/PNG>
driving_license=<image file, JPG/PNG>
aadhar_card=<image file, JPG/PNG>
pan_card=<image file, JPG/PNG>
registration_cert=<image file, JPG/PNG>
vehicle_insurance=<image file, JPG/PNG>
vehicle_permit=<image file, JPG/PNG>
capacity=<int>
category=<DRINKING|NON_DRINKING|BOTH>
csrfmiddlewaretoken=<token>
```

---

## URL Naming Conventions

| URL Name | App | Usage in Templates |
|---|---|---|
| `home` | Customer | `{% url 'home' %}` |
| `booking` | Customer | `{% url 'booking' %}` |
| `driver_detail` | Customer | `{% url 'driver_detail' %}` |
| `profile` | Customer | `{% url 'profile' %}` (Customer) |
| `notification` | Customer | `{% url 'notification' %}` |
| `login` | Customer | `{% url 'login' %}` |
| `register` | Customer | `{% url 'register' %}` |
| `logout` | Customer | `{% url 'logout' %}` |
| `forgot_password` | Customer | `{% url 'forgot_password' %}` |
| `Home` | Supplier | `{% url 'Home' %}` |
| `Login_page` | Supplier | `{% url 'Login_page' %}` |
| `Register_page` | Supplier | `{% url 'Register_page' %}` |
| `Logout_page` | Supplier | `{% url 'Logout_page' %}` |
| `Earning` | Supplier | `{% url 'Earning' %}` |
| `Order_List` | Supplier | `{% url 'Order_List' %}` |
| `Notification` | Supplier | `{% url 'Notification' %}` |
| `Profile` | Supplier | `{% url 'Profile' %}` |
| `toggle_availability` | Supplier | `{% url 'toggle_availability' %}` |
| `role_selection` | Root | `{% url 'role_selection' %}` |

**Inconsistency Note:** Customer URL names are `snake_case`, Supplier URL names are `TitleCase`. Should be standardized.

---

## Missing API Features

| Feature | Current State | Impact |
|---|---|---|
| Payment processing endpoint | No endpoint exists | Payments cannot be made |
| Order history endpoint | No dedicated list view for all customer orders | Customers can't see past orders |
| Supplier rating/review | No endpoint | Rating is hardcoded "4.5" |
| Admin notifications on document upload | No endpoint | Admin must check admin panel manually |
| Mobile API (REST/JSON) | Not implemented | No mobile app possible without adding DRF views |
