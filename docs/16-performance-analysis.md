# 16 — Performance Analysis

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [08-database-design.md](08-database-design.md) · [05-system-architecture.md](05-system-architecture.md) · [17-improvement-suggestions.md](17-improvement-suggestions.md)

---

## Performance Strengths

### 1. Async Email via Celery
All registration confirmation emails are dispatched via `send_email_task.delay()`, ensuring SMTP latency (~200-500ms per email) never blocks the HTTP response. This is the most important performance decision in the codebase.

### 2. `select_related` on Critical Queries
The supplier order views use `select_related` to prefetch related objects in a single JOIN query:

```python
# Supplier/views.py
OrderDetail.objects.filter(...).select_related('user', 'location', 'driver', 'tanker')
```

This prevents N+1 queries when rendering order lists with related user, location, driver, and tanker information.

### 3. Gunicorn Multi-Worker
Production uses Gunicorn with 3 workers, enabling concurrent request handling. SQLite in development is the bottleneck here — PostgreSQL in production removes that constraint.

### 4. WhiteNoise for Static Files
Static files are served by WhiteNoise directly from Gunicorn, bypassing Python for static requests. This is significantly faster than serving through Django's development server.

---

## Performance Issues

### Issue 1 — No Pagination

**Impact:** High (as data grows)  
**Affected pages:** Order List, Notification pages, Earning page

```python
# Supplier/views.py — All notifications fetched
Notification.objects.filter(supplier=user).order_by('-timestamp')

# Customer/views.py — All notifications fetched
Notification.objects.filter(customer=user, initiated_by='supplier').order_by('-timestamp')

# Supplier/views.py — All pending orders in pincode fetched
OrderDetail.objects.filter(order_status='Pending', location__pincode=supplier_pincode)
```

A busy market with 500+ orders per supplier pincode or 1000+ notifications would cause slow page loads and high memory usage.

**Fix:** Use Django's `Paginator` class, e.g., 20 items per page.

---

### Issue 2 — No Database Indexes on Hot Filter Columns

**Impact:** High (as OrderDetail table grows)

The most frequently used filter:
```python
OrderDetail.objects.filter(order_status='Pending', location__pincode=supplier_pincode)
OrderDetail.objects.filter(order_status='Delivered', driver=driver)
```

Neither `order_status` nor `driver_id` nor `location__pincode` has a `db_index=True` on the model fields. On a large table, Django will do full table scans for every order list/dashboard/earning view load.

**Current model definition:**
```python
class OrderDetail(models.Model):
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    driver = models.ForeignKey(DriverDetail, on_delete=models.SET_NULL, null=True)
    # No db_index=True on either field
```

**Fix:**
```python
order_status = models.CharField(..., db_index=True)
# driver_id FK is indexed by default (Django auto-indexes FKs)
# For pincode:
# customer_locationdetail.pincode should have db_index=True
```

---

### Issue 3 — Earnings View Makes 7 Separate Database Queries

**Impact:** Medium  
**Location:** `Supplier/views.py:336-370`

```python
for i in range(7):
    day = today - timedelta(days=i)
    orders = OrderDetail.objects.filter(
        driver=driver,
        order_status='Delivered',
        order_date__gte=start_time,
        order_date__lt=end_time
    )
    total = orders.aggregate(total=Sum('price'))['total'] or 0
```

This runs **7 queries** (one per day) plus a count query and order_times query per day — approximately **14-21 database queries** for a single page load.

**Fix:** Use a single query with `annotate()` grouping by date:
```python
from django.db.models.functions import TruncDate

OrderDetail.objects.filter(
    driver=driver, order_status='Delivered', order_date__gte=seven_days_ago
).annotate(day=TruncDate('order_date')).values('day').annotate(
    total=Sum('price'), count=Count('id')
).order_by('-day')
```

---

### Issue 4 — Daily Email Task Bug Causes Near-Zero Throughput

**Impact:** High (feature completely broken)  
**Location:** `Customer/tasks.py:20-38` and `Supplier/tasks.py:20-38`

```python
@shared_task
def send_mail_every_day():
    users = CustomUser.objects.all()
    for user in users:
        subject = f"Good Evening, {user.first_name}!"
        message = f"..."
        # ← BUG: send_mail() is OUTSIDE the for loop
    try:
        send_mail(subject, message, EMAIL_HOST_USER, [user.email])
    except ...:
```

The `send_mail()` call is at the same indentation as the `try` block — outside the `for` loop. Only the last user's email/subject/message variables are used.

**Additionally:** Even if fixed, sending thousands of individual emails synchronously inside a single Celery task would be slow. Should use Celery groups or `send_mass_mail()`.

---

### Issue 5 — Dashboard Data Function Is a View, Not a Helper

**Impact:** Low-Medium  
**Location:** `Supplier/views.py:242-276`

`get_supplier_dashboard_data()` is decorated with `@csrf_exempt` and `@login_required` — it's treated as a view but it just returns a dict:

```python
@csrf_exempt
@login_required(login_url="Login_page")
def get_supplier_dashboard_data(request):
    data = {...}
    ...
    return data  # Returns dict, not HttpResponse!
```

This function is called internally from `Supp_Home()` and `notifications()`. The view decorators have no effect (the function is never routed directly), but the function signature is confusing. If someone accidentally routes a URL to it, it would return a dict (not an `HttpResponse`), causing a crash.

---

### Issue 6 — Supplier Home Makes Multiple Separate Queries Without Optimization

**Impact:** Medium  
**Location:** `Supplier/views.py:280-307`

```python
def Supp_Home(request):
    driver_detail = DriverDetail.objects.get(user=request.user)    # Query 1
    if supplier.is_available:
        pending = OrderDetail.objects.filter(                        # Query 2
            order_status='Pending', location__pincode=supplier_pincode
        ).select_related('user', 'location', 'tanker')
    
    recent_orders = OrderDetail.objects.filter(                      # Query 3
        order_status='Accepted', driver=driver_detail
    ).select_related('user', 'location', 'driver', 'tanker').first()
    
    dashboard_data = get_supplier_dashboard_data(request)            # Queries 4-6+
```

Plus session lookup. Approximately 6-8 queries per dashboard load.

---

### Issue 7 — No HTTP Caching Headers

No `Cache-Control`, `ETag`, or `Last-Modified` headers are set on any response. Every page load is a full dynamic render with no browser caching benefit.

For static pages like the supplier profile (changes rarely), this means unnecessary repeated database queries.

---

### Issue 8 — Celery Beat Schedule Overwritten

**Impact:** Medium (feature reliability)  
**Location:** `Water_Tanker_Project/celery.py:17-28`

```python
app.conf.beat_schedule = {
    'send_mail_every_day': {'task': 'Customer.tasks.send_mail_every_day', ...}
}
app.conf.beat_schedule = {                      # ← Overwrites above!
    'send_mail_every_day': {'task': 'Supplier.tasks.send_mail_every_day', ...}
}
```

Only one task fires (Supplier task). Customer daily email never runs.

---

## Database Query Count by Page

| Page | Estimated Queries | With Fix |
|---|---|---|
| Customer Home | 1-2 | — |
| Customer Booking (GET) | 3-4 | — |
| Customer Booking (POST) | 4 writes | — |
| Customer Driver Detail | 2-3 | — |
| Customer Notifications | 2-3 | 2-3 + pagination |
| Supplier Dashboard | 6-8 | 4-5 with caching |
| Supplier Order List | 4-5 | 3-4 |
| **Supplier Earnings** | **14-21** | **2-3** (single annotated query) |
| Supplier Profile | 5-6 | 3-4 |
| Supplier Notifications | 3-4 | 3-4 + pagination |

---

## Performance Improvement Priority

| Priority | Issue | Effort | Impact |
|---|---|---|---|
| P1 | Fix Celery daily email bug | Low | High |
| P1 | Fix Celery beat schedule overwrite | Low | High |
| P2 | Add `db_index` to `order_status`, `pincode` | Low | High |
| P2 | Add pagination to all list views | Medium | High |
| P3 | Optimize earnings query (7 → 1 query) | Medium | Medium |
| P3 | Refactor `get_supplier_dashboard_data` as a helper | Low | Medium |
| P4 | Add query result caching for supplier profile | Medium | Low |
| P4 | Add HTTP caching headers | Low | Low |
