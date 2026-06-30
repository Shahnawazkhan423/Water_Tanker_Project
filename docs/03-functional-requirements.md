# 03 — Functional Requirements

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [02-business-requirements.md](02-business-requirements.md) · [07-module-analysis.md](07-module-analysis.md) · [09-api-documentation.md](09-api-documentation.md)

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Fully implemented |
| ⚠️ | Partially implemented or has known issues |
| ❌ | Not implemented (model/stub exists) |
| 🔴 | Bug confirmed in code |

---

## FR-01: User Registration — Customer

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-01.1 | System accepts first name, last name, phone number (10 digits, starts 6-9), Gmail address, password, optional profile image | ✅ | `Customer/forms.py: UserDetailForm` |
| FR-01.2 | System accepts delivery address: address line, street, landmark (optional), city, state, pincode (6 digits) | ✅ | `Customer/forms.py: LocationDetailForm` |
| FR-01.3 | System rejects duplicate Gmail addresses | ✅ | `Customer/views.py: register_view` (checks `CustomerProfile`) |
| FR-01.4 | System sets `user_type='customer'` automatically | ✅ | `Customer/forms.py: UserDetailForm.save()` |
| FR-01.5 | System creates `CustomerProfile` and `LocationDetail` records alongside `CustomUser` | ✅ | `Customer/views.py: register_view` |
| FR-01.6 | System sends registration confirmation email asynchronously | ✅ | `Customer/tasks.py: send_email_task.delay()` |
| FR-01.7 | System redirects to login after successful registration | ✅ | `Customer/views.py` |

---

## FR-02: User Registration — Supplier

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-02.1 | System accepts same personal info as customer registration | ✅ | `Supplier/forms.py: SupplierRegistrationForm` |
| FR-02.2 | System accepts supplier location (same fields as customer) | ✅ | `Supplier/forms.py: SupplierLocationDetailForm` |
| FR-02.3 | System rejects duplicate Gmail addresses | ✅ | `Supplier/views.py: register_view` |
| FR-02.4 | System sets `user_type='supplier'` automatically | ✅ | `Supplier/forms.py: SupplierRegistrationForm.save()` |
| FR-02.5 | System auto-creates `SupplierProfile` (is_available=False) | ✅ | `Supplier/views.py: register_view` |
| FR-02.6 | System auto-creates `DriverAvailability` (status='unavailable') | ✅ | `Supplier/views.py: register_view` |
| FR-02.7 | System auto-creates `DriverDetail` linked to new user | ✅ | `Supplier/views.py: register_view` |
| FR-02.8 | System immediately authenticates and redirects supplier to tanker registration | ✅ | `Supplier/views.py: register_view` |
| FR-02.9 | System sends registration confirmation email asynchronously | ✅ | `Supplier/tasks.py: send_email_task.delay()` |

---

## FR-03: Tanker & Document Registration (Supplier)

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-03.1 | Supplier uploads a named tanker document set (7 files: profile photo, driving license, Aadhar, PAN, RC, insurance, permit) | ✅ | `Supplier/forms.py: WaterTankerForm` |
| FR-03.2 | System validates file types — only JPG/PNG allowed | ✅ | `Supplier/forms.py: _clean_file_field()` |
| FR-03.3 | Supplier selects tanker capacity (1000/2000/5000/10000 L) and category (Drinking/Non-Drinking/Both) | ✅ | `Supplier/forms.py: SupplierTankerDetailForm` |
| FR-03.4 | `WaterTankerDocument.is_approved` defaults to 'Pending' | ✅ | `Supplier/models.py: WaterTankerDocument` |
| FR-03.5 | System links document to tanker and tanker to driver | ✅ | `Supplier/views.py: tanker_detail_view` |
| FR-03.6 | System deletes `supplier_email` session variable after successful registration | ✅ | `Supplier/views.py: tanker_detail_view` |

---

## FR-04: Authentication

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-04.1 | Customer logs in via email + password at `/Customer/Login/` | ✅ | `Customer/views.py: login_view` |
| FR-04.2 | System enforces `user_type == 'customer'` on customer login | ✅ | `Customer/views.py: login_view` |
| FR-04.3 | Supplier logs in via email + password at `/Supplier/Login/` | ✅ | `Supplier/views.py: login_view` |
| FR-04.4 | System enforces `user_type == 'supplier'` on supplier login | 🔴 | **BUG:** checks `isinstance(user, CustomUser)` only — no role guard |
| FR-04.5 | Customer logout clears session and redirects to customer login | ✅ | `Customer/views.py: logout_view` |
| FR-04.6 | Supplier logout clears session and renders supplier login | ✅ | `Supplier/views.py: logout_view` |
| FR-04.7 | Authentication uses email as username field | ✅ | `UserManagement/backends.py: EmailBackend` |

---

## FR-05: Forgot Password

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-05.1 | Customer requests password reset by email | ✅ | `Customer/views.py: forgot_password` |
| FR-05.2 | System generates UUID v4 token and stores in `CustomerProfile.forgot_password_token` | ✅ | `Customer/views.py: forgot_password` |
| FR-05.3 | System sends email with reset link | ✅ | `Customer/helper.py: send_forgot_password_mail()` |
| FR-05.4 | Customer clicks link and enters new password | ✅ | `Customer/views.py: reset_password` |
| FR-05.5 | System clears token after successful reset | ✅ | `Customer/views.py: reset_password` |
| FR-05.6 | Reset link expires | 🔴 | **BUG:** No expiry — token valid forever |
| FR-05.7 | Reset link contains correct production URL | 🔴 | **BUG:** Hardcoded `http://127.0.0.1:8000` |

---

## FR-06: Customer Home & Navigation

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-06.1 | Customer home view enforces login and correct user type | ✅ | `Customer/views.py: home` |
| FR-06.2 | Customer sees navigation to Booking, Driver Detail, Notifications, Profile | ✅ | Template-based navigation |

---

## FR-07: Water Tanker Booking

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-07.1 | Customer pre-fills personal info (name, phone) from their profile | ✅ | `BookingUserForm(instance=request.user)` |
| FR-07.2 | Customer selects tanker capacity with price shown | ✅ | `Customer/forms.py: TankerDetailForm` |
| FR-07.3 | Customer selects water category | ✅ | `TankerDetailForm` |
| FR-07.4 | Customer provides delivery address (pre-filled from CustomerProfile) | ✅ | `Customer/views.py: booking` (GET path) |
| FR-07.5 | System calculates and stores total price | ✅ | `Customer/views.py: booking` |
| FR-07.6 | System creates `OrderDetail` with status='Pending', no driver assigned | ✅ | `Customer/views.py: booking` |
| FR-07.7 | Booking operation is atomic (all-or-nothing) | ✅ | `with transaction.atomic()` |
| FR-07.8 | Booking creates new `TankerDetail` per order (not reusing supplier's) | ⚠️ | Design inconsistency — see [17-improvement-suggestions.md](17-improvement-suggestions.md) |

---

## FR-08: Order Tracking — Customer

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-08.1 | Customer sees orders with status Accepted or "On The Way" on driver detail page | ✅ | `Customer/views.py: driver_detail` |
| FR-08.2 | Customer can cancel order if status is Pending or Accepted | ✅ | `Customer/views.py: cancel_order` |
| FR-08.3 | Cancellation is blocked if order is On the Way or Delivered | ✅ | `Customer/views.py: cancel_order` |
| FR-08.4 | Cancellation fires signal → creates supplier notification | ⚠️ | Signal fires but `customer_user.name` attribute doesn't exist (should be `first_name`) — **BUG in receiver** |

---

## FR-09: Supplier Availability

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-09.1 | Supplier toggles availability via POST endpoint | ✅ | `Supplier/views.py: toggle_availability` |
| FR-09.2 | Toggle requires approved documents | ✅ | `Supplier/views.py: toggle_availability` |
| FR-09.3 | Going available creates a new `DriverAvailability` record (status='available') | ✅ | `Supplier/views.py: toggle_availability` |
| FR-09.4 | Going unavailable closes last availability record (sets `end_time`, status='unavailable') | ✅ | `Supplier/views.py: toggle_availability` |
| FR-09.5 | Tanker availability (`TankerDetail.available`) mirrors supplier availability | ✅ | `Supplier/views.py: toggle_availability` |
| FR-09.6 | Returns JSON response (used by JavaScript on dashboard) | ✅ | `JsonResponse` |

---

## FR-10: Supplier Dashboard

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-10.1 | Shows pending orders in supplier's pincode when available | ✅ | `Supplier/views.py: Supp_Home` |
| FR-10.2 | Shows most recent accepted order | ✅ | `Supplier/views.py: Supp_Home` |
| FR-10.3 | Shows orders accepted count, completed count | ✅ | `Supplier/views.py: get_supplier_dashboard_data` |
| FR-10.4 | Shows revenue from last 24 hours | ✅ | `Supplier/views.py: get_supplier_dashboard_data` |
| FR-10.5 | Shows current availability status | ✅ | `Supplier/views.py: Supp_Home` |

---

## FR-11: Order Management — Supplier

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-11.1 | Supplier sees pending orders in their pincode (when available) | ✅ | `Supplier/views.py: order_list` |
| FR-11.2 | Supplier sees their own accepted and on-the-way orders | ✅ | `Supplier/views.py: order_list` |
| FR-11.3 | Supplier can accept a pending order → fires notification to customer | ✅ | `Supplier/views.py: update_order_status` |
| FR-11.4 | Supplier can cancel a pending order → fires notification to customer | ✅ | `Supplier/views.py: update_order_status` |
| FR-11.5 | Supplier can mark order "On the Way" → fires notification to customer | ✅ | `Supplier/views.py: update_order_status` |
| FR-11.6 | Supplier can mark order "Delivered" → fires notification to customer | ✅ | `Supplier/views.py: update_order_status` |

---

## FR-12: Notifications

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-12.1 | Customer sees notifications from supplier (accepted, on way, delivered, cancelled) | ✅ | `Customer/views.py: notification` |
| FR-12.2 | Supplier sees notifications from customer (order cancelled) | ✅ | `Supplier/views.py: notifications` |
| FR-12.3 | Notifications ordered by newest first | ✅ | `.order_by('-timestamp')` |
| FR-12.4 | Customer can delete individual notifications | ✅ | `Customer/views.py: delete_notification` |
| FR-12.5 | Supplier can delete individual notifications | ✅ | `Supplier/views.py: delete_notification` |
| FR-12.6 | Unread notifications are marked as read | ❌ | `is_read` field exists but never set to True |

---

## FR-13: Earnings — Supplier

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-13.1 | Today's earnings (total amount, orders completed, total orders) | ✅ | `Supplier/views.py: earning` |
| FR-13.2 | Last 7 days earnings (per day: time range, amount, order count) | ✅ | `Supplier/views.py: earning` |
| FR-13.3 | Total earnings (sum of 7-day period) | ✅ | `Supplier/views.py: earning` |

---

## FR-14: Profile Management

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-14.1 | Customer views their profile information | ✅ | `Customer/views.py: profile` |
| FR-14.2 | Customer uploads new profile image | ✅ | `Customer/views.py: update_profile_image` |
| FR-14.3 | Supplier views full profile (user info, driver details, tanker, documents, location) | ✅ | `Supplier/views.py: profile` |
| FR-14.4 | Supplier profile shows "joined since" in human-readable format | ✅ | `Supplier/utils.py: human_readable_joined_date()` |
| FR-14.5 | Supplier profile shows completed orders count | ✅ | `Supplier/views.py: profile` |
| FR-14.6 | Supplier profile shows rating | ⚠️ | Hardcoded "4.5" — no real rating system |
| FR-14.7 | Supplier uploads new profile image | ✅ | `Supplier/views.py: update_profile_image` |

---

## FR-15: Async Email

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-15.1 | Registration email sent via Celery task | ✅ | `Customer/tasks.py`, `Supplier/tasks.py` |
| FR-15.2 | Daily "Good Evening" email to all users at 19:00 IST | ⚠️ | **BUG:** Loop logic broken — only last user gets email. Also, Celery beat schedule is overwritten (only one fires) |

---

## FR-16: Admin

| ID | Requirement | Status | Location |
|---|---|---|---|
| FR-16.1 | Admin manages `CustomUser` records | ✅ | `UserManagement/admin.py: CustomUserAdmin` |
| FR-16.2 | Admin approves/rejects supplier documents | ✅ | Via Django Admin on `WaterTankerDocument.is_approved` field |
| FR-16.3 | Admin receives notification when documents are submitted | ❌ | Not implemented |
