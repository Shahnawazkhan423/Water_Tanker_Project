# 17 — Improvement Suggestions

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [15-security-analysis.md](15-security-analysis.md) · [16-performance-analysis.md](16-performance-analysis.md) · [18-development-roadmap.md](18-development-roadmap.md)

---

## Priority Classification

| Level | Meaning |
|---|---|
| 🔴 P0 — Critical | Must fix before production deployment |
| 🟠 P1 — High | Fix in current or next sprint |
| 🟡 P2 — Medium | Fix in next 1-2 months |
| 🟢 P3 — Low | Fix when time allows |
| 🔵 Enhancement | New feature or architectural improvement |

---

## P0 — Critical Fixes (Must Fix Before Production)

### S-01: Remove `.env` from Git History and Rotate All Secrets
**Problem:** `.env` with `SECRET_KEY`, email credentials, and DB password is committed to git.  
**Action:**
1. `git rm --cached .env` + add to `.gitignore`
2. Use `git-filter-repo` to purge from history
3. Generate new `SECRET_KEY` (Django provides `django.core.management.utils.get_random_secret_key()`)
4. Revoke and regenerate Gmail App Password
5. Create `.env.example` with placeholder values

### S-02: Fix Password Reset URL
**Problem:** `Customer/helper.py:8` hardcodes `http://127.0.0.1:8000`.  
**Action:** Replace with:
```python
from django.urls import reverse
reset_link = request.build_absolute_uri(
    reverse('reset_password', kwargs={'token': token})
)
```

### S-03: Fix Supplier Login Role Guard
**Problem:** `Supplier/views.py:144` allows any user type to log in as supplier.  
**Action:** Change condition to:
```python
if user is not None and user.user_type == 'supplier':
```

### S-04: Fix AttributeError in Customer Cancel Receiver
**Problem:** `Customer/receivers.py:9` uses `customer_user.name` which doesn't exist.  
**Action:** Change to:
```python
message=f"Order ID {order_instance.id} has been cancelled by customer {customer_user.first_name} {customer_user.last_name}."
```

---

## P1 — High Priority

### S-05: Remove `@csrf_exempt` from All Non-API Views
**Problem:** CSRF protection is disabled on login, registration, booking, and most supplier views.  
**Action:** Remove `@csrf_exempt` decorators. Ensure all POST forms include `{% csrf_token %}` (most already do).

### S-06: Fix Celery Daily Email Task Bug
**Problem:** `send_mail()` call is outside the user loop — only last user receives email.  
**Location:** `Customer/tasks.py:35`, `Supplier/tasks.py:35`  
**Action:** Move the `send_mail()` call inside the `for` loop:
```python
for user in users:
    subject = f"Good Evening, {user.first_name}!"
    message = f"..."
    try:
        send_mail(subject, message, EMAIL_HOST_USER, [user.email], fail_silently=False)
    except Exception as e:
        logger.error(f"Email to {user.email} failed: {e}")
```

### S-07: Fix Celery Beat Schedule Overwrite
**Problem:** Second `app.conf.beat_schedule` assignment overwrites the first. Only Supplier task fires.  
**Location:** `Water_Tanker_Project/celery.py:17-28`  
**Action:** Merge both schedules (or since the tasks are identical, use one):
```python
app.conf.beat_schedule = {
    'send_mail_every_day': {
        'task': 'Customer.tasks.send_mail_every_day',  # or create one shared task
        'schedule': crontab(hour=19, minute=0),
    },
}
```

### S-08: Add Token Expiry to Password Reset
**Problem:** Reset tokens are valid forever.  
**Action:** Add `forgot_password_token_created_at = DateTimeField(null=True, blank=True)` to `CustomerProfile`. In `reset_password` view, reject tokens older than 1 hour.

### S-09: Set `SESSION_COOKIE_SECURE = True` in Production
**Problem:** Session cookies sent over HTTP.  
**Action:** Use environment variable:
```python
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
```
Set `SESSION_COOKIE_SECURE=True` in production `.env`.

### S-10: Add `@login_required` to `cancel_order`
**Location:** `Customer/views.py:211`  
**Action:** Add `@login_required(login_url='login')` decorator.

---

## P2 — Medium Priority

### P-01: Consolidate Duplicate `LocationDetail` Models
**Problem:** Two identical models in Customer and Supplier apps — separate DB tables, no cross-join.  
**Action:** Move `LocationDetail` to `UserManagement` app. Update all FK references. Create a single migration.

### P-02: Consolidate Duplicate Celery Tasks
**Problem:** `send_email_task` and `send_mail_every_day` are copy-pasted in both apps.  
**Action:** Create a single shared task (e.g., in `UserManagement/tasks.py`). Import from there in both apps.

### P-03: Fix Booking to Reference Supplier's Existing Tanker
**Problem:** `Customer/views.py:booking()` creates a new phantom `TankerDetail` row per booking instead of linking to the supplier's real tanker.  
**Action:** Remove `TankerDetailForm` from the booking page. Instead, let the customer select capacity/category preferences. When a supplier accepts, link `OrderDetail.tanker` to the supplier's actual `TankerDetail`.

### P-04: Add Database Indexes
**Action:** Add `db_index=True` to:
```python
# Customer/models.py
class OrderDetail(models.Model):
    order_status = models.CharField(..., db_index=True)

# Customer/models.py  
class LocationDetail(models.Model):
    pincode = models.CharField(..., db_index=True)
```

### P-05: Add Pagination to All List Views
**Action:** Apply `Paginator` to:
- Notification lists (Customer + Supplier)
- Order list (Supplier)
- Earnings history (if list-based)
- Admin order management

### P-06: Optimize Earnings Query (7 Queries → 1)
**Action:** Replace the day-by-day loop with a single annotated query using `TruncDate`.

### P-07: Remove Unused Packages
**Action:** Remove from `requirements.txt`:
- `python-dotenv`
- `django-crispy-forms`
- `crispy-bootstrap5`
- `djangorestframework`
- `django-model-utils`
- `mysqlclient` (unless MySQL is planned)
- `dj-database-url` (unless `DATABASE_URL` pattern is adopted)

### P-08: Remove Debug Print Statements
**Location:** `Customer/views.py:231, 248`  
**Action:** Remove all `print()` statements. Use `import logging; logger = logging.getLogger(__name__)` with `logger.debug()`.

---

## P3 — Low Priority

### P-09: Implement Password Reset for Suppliers
**Problem:** Forgot-password flow is only implemented for Customers. Suppliers have no self-service password recovery.  
**Action:** Mirror the Customer forgot/reset password flow for Suppliers.

### P-10: Implement `is_read` for Notifications
**Problem:** `Notification.is_read` field exists but is never set to True.  
**Action:** Set `is_read=True` when the notifications page is visited. Add unread count badges to the nav.

### P-11: Standardize Template and URL Naming Conventions
**Problem:** Customer templates use `lowercase.html`, Supplier uses `TitleCase.html`. Customer URL names use `snake_case`, Supplier uses `TitleCase`.  
**Action:** Standardize to `snake_case` for URL names and `lowercase.html` for template files.

### P-12: Add `docker-compose.yml`
**Problem:** Local development requires manually starting Django, Redis, and Celery.  
**Action:** Create `docker-compose.yml` with services: web, redis, celery_worker, celery_beat.

### P-13: Add `.env.example`
**Action:** Create `.env.example`:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DB_ENGINE=django.db.backends.postgresql
DB_NAME=water_tanker
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

### P-14: Fix Session Age Inconsistency
**Problem:** `SESSION_COOKIE_AGE=3600` (settings) vs `max_age=86400` (middleware).  
**Action:** Use `settings.SESSION_COOKIE_AGE` in the middleware instead of hardcoding 86400.

---

## 🔵 Enhancement Suggestions

### E-01: Implement Payment Gateway Integration
The `Payment` model exists but no payment flow is implemented. Integrate a payment gateway (Razorpay, Stripe, or PayU) to:
- Process payments at booking
- Generate receipts
- Handle refunds on cancellation

### E-02: Add Real-Time Notifications (WebSockets)
Current notifications are pull-based (page refresh required). Add Django Channels + WebSocket support to push notifications to connected clients instantly.

### E-03: Implement Geo-Distance Based Order Matching
Currently, order matching is pincode-only. The `latitude`/`longitude` fields and `geopy`/`haversine` utilities are in place but unused. Implement radius-based matching (e.g., orders within 5km of supplier).

### E-04: Add Customer Order History Page
Customers currently cannot see past (Delivered/Canceled) orders. Add a dedicated order history view.

### E-05: Implement Real Supplier Rating System
The rating is hardcoded "4.5" in the supplier profile. Implement a proper rating model where customers can rate suppliers after delivery.

### E-06: Add Admin Dashboard for Document Approval
Currently, admins must navigate through the Django Admin raw interface to approve documents. Build a dedicated admin UI page for reviewing submitted documents with approve/reject buttons and notification to supplier on decision.

### E-07: Add REST API Layer
Install and configure Django REST Framework properly to support a future mobile application. Implement JWT authentication, OrderDetail serializers, and key endpoints.

### E-08: Implement Order Timeout
If an order sits in 'Pending' status for more than X minutes with no supplier accepting (because no available supplier in pincode), notify the customer and offer options (wait, change location, cancel).

### E-09: Switch to PostgreSQL in Development
Using SQLite in dev and PostgreSQL in production creates risk of schema/query behavior differences. Use PostgreSQL (via Docker) in all environments.

### E-10: Add Test Coverage
All `tests.py` files are empty stubs. Implement:
- Unit tests for form validation
- Unit tests for pricing logic
- Integration tests for registration/booking/order flows
- Signal/receiver tests for notification creation
