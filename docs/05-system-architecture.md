# 05 — System Architecture

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [06-folder-structure.md](06-folder-structure.md) · [07-module-analysis.md](07-module-analysis.md) · [12-data-flow.md](12-data-flow.md)

---

## Architecture Pattern

The application follows **Django's MVT (Model-View-Template)** pattern, which is a variant of MVC:

| Layer | Django Equivalent | Responsibility |
|---|---|---|
| Model | `models.py` in each app | Data definition, ORM queries, business data rules |
| View | `views.py` in each app | Request handling, business logic, template selection |
| Template | `*.html` files | Presentation, rendering context data |

There is **no service layer** — business logic lives directly in view functions.

There is **no REST API** for external consumers — all responses are server-rendered HTML (except one JSON endpoint for the availability toggle).

---

## High-Level Architecture Diagram

```
┌───────────────────────────────────────────────────────────────┐
│                         Browser / Client                       │
│   Bootstrap 5 · Bootstrap Icons · FontAwesome · Vanilla JS    │
└───────────────────────────┬───────────────────────────────────┘
                            │ HTTP (port 80/443)
┌───────────────────────────▼───────────────────────────────────┐
│              Gunicorn WSGI Server (3 workers)                  │
│              Listens on 0.0.0.0:8000                          │
│              Water_Tanker_Project.wsgi:application            │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    Django Middleware Stack                      │
│  1. SecurityMiddleware                                         │
│  2. SessionMiddleware (default)                               │
│  3. MultiAppSessionMiddleware (custom — role-based sessions)  │
│  4. CommonMiddleware                                          │
│  5. CsrfViewMiddleware                                        │
│  6. AuthenticationMiddleware                                  │
│  7. MessageMiddleware                                         │
│  8. XFrameOptionsMiddleware                                   │
└───────┬──────────────────┬─────────────────┬─────────────────┘
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼────────────────┐
│   Customer   │  │    Supplier     │  │   UserManagement     │
│     App      │  │      App        │  │       App            │
│              │  │                 │  │                      │
│ ┌──────────┐ │  │ ┌─────────────┐ │  │ ┌──────────────────┐ │
│ │  Models  │ │  │ │   Models    │ │  │ │    CustomUser    │ │
│ │ ─────── │ │  │ │ ──────────  │ │  │ │   EmailBackend   │ │
│ │ Profile  │ │  │ │SupplierProf │ │  │ │  role_selection  │ │
│ │ Order    │ │  │ │DriverDetail │ │  │ └──────────────────┘ │
│ │ Payment  │ │  │ │ TankerDetail│ │  └──────────────────────┘
│ │ Notif.   │ │  │ │ WaterDoc    │ │
│ └──────────┘ │  │ └─────────────┘ │
└──────────────┘  └─────────────────┘
        │                  │
        └─────────┬────────┘
                  │ ORM / SQL
┌─────────────────▼─────────────────────────────────────────────┐
│         Database (SQLite dev / PostgreSQL prod)                │
└───────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│               Celery Async / Scheduled Tasks                   │
│                                                                │
│  ┌──────────────────┐    ┌──────────────────────────────────┐ │
│  │  Celery Worker   │◄───│  Redis Broker (127.0.0.1:6379/0) │ │
│  │  (send emails)   │    └──────────────────────────────────┘ │
│  └────────┬─────────┘    ┌──────────────────────────────────┐ │
│           │              │ Redis Backend (127.0.0.1:6379/1)  │ │
│  ┌────────▼─────────┐    └──────────────────────────────────┘ │
│  │  Celery Beat     │                                         │
│  │ (19:00 IST daily)│                                         │
│  └──────────────────┘                                         │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                Gmail SMTP (smtp.gmail.com:587)                  │
│                   Email delivery (TLS)                         │
└────────────────────────────────────────────────────────────────┘
```

---

## Request Routing Architecture

```
GET/POST /
  └── UserManagement.views.role_selection → Landing page

GET/POST /Customer/*
  └── Customer.urls → Customer.views.*

GET/POST /Supplier/*
  └── Supplier.urls → Supplier.views.*

GET /admin/*
  └── Django Admin
```

---

## Session Architecture (Custom)

The `MultiAppSessionMiddleware` intercepts every request and routes it to a different session backend based on URL prefix:

```
Request path starts with /Supplier/
  → Cookie name:    'supplier_sessionid'
  → Backend engine: 'django.contrib.sessions.backends.cache'  (Redis)

Request path starts with /Customer/
  → Cookie name:    'customer_sessionid'
  → Backend engine: 'django.contrib.sessions.backends.db'     (Database)

All other paths
  → Cookie name:    default ('sessionid')
  → Backend engine: 'django.contrib.sessions.backends.db'
```

This means a single browser can have **two simultaneous sessions** — one for Customer, one for Supplier — without conflicts.

---

## Signal / Event Architecture

Order state changes are communicated between apps using Django's **custom signal** pattern. This decouples the views from the notification creation logic.

```
Customer App                    Supplier App
─────────────                   ────────────
cancel_order (view)             update_order_status (view)
  │                               │
  │ fires                         │ fires (4 signals)
  ▼                               ▼
order_canceled_by_customer      order_accepted_by_supplier
  │                             order_canceled_by_supplier
  │                             order_on_the_way_by_supplier
  │                             order_delievery_by_supplier
  │                               │
  ▼                               ▼
Customer/receivers.py           Supplier/receivers.py
create_cancel_notification_    create_*_notification_*()
  for_supplier()
  │                               │
  ▼                               ▼
Customer.Notification.objects   Customer.Notification.objects
  .create(initiated_by=          .create(initiated_by=
    'customer')                    'supplier')
```

---

## Authentication Architecture

```
Login Request
  │
  ▼
django.contrib.auth.authenticate()
  │
  ├── Try: UserManagement.backends.EmailBackend
  │     CustomUser.objects.get(email=email)
  │     user.check_password(password) → True → return user
  │
  └── Try: django.contrib.auth.backends.ModelBackend (fallback)

Post-authenticate:
  Customer login:  checks user.user_type == 'customer'
  Supplier login:  checks isinstance(user, CustomUser)  ← MISSING role guard
```

---

## Celery Architecture

```
Django App
  │
  │ send_email_task.delay(to, subject, message)
  ▼
Redis Broker (db 0)  ←── Task queue
  │
  ▼
Celery Worker  ─────── Picks task ──► send_mail() → Gmail SMTP
  │
  │ Result stored
  ▼
Redis Backend (db 1)

─────────────────────────────────────

Celery Beat (scheduler)
  │
  │ Every day at 19:00 IST
  ▼
Fires: Supplier.tasks.send_mail_every_day  ← BUG: Customer task overwritten
```

---

## Deployment Architecture

```
┌─────────────────────────────────────┐
│         Docker Container            │
│  ┌────────────────────────────────┐ │
│  │  Stage 1: Builder              │ │
│  │  - Install build deps          │ │
│  │  - pip wheel all requirements  │ │
│  └────────────────────────────────┘ │
│  ┌────────────────────────────────┐ │
│  │  Stage 2: Runtime              │ │
│  │  - Minimal runtime deps        │ │
│  │  - Install pre-built wheels    │ │
│  │  - Copy project files          │ │
│  │  - Run as 'appuser' (non-root) │ │
│  │  - EXPOSE 8000                 │ │
│  │  CMD:                          │ │
│  │    migrate                     │ │
│  │    collectstatic               │ │
│  │    gunicorn (3 workers)        │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘

WhiteNoise serves /static/ files directly (no nginx needed for static)
Redis must be a separate container or managed service
```

---

## Design Patterns Used

| Pattern | Where Used | Purpose |
|---|---|---|
| **MVT** | Entire application | Standard Django architecture |
| **Custom Signal/Receiver** | Order state change notifications | Decouples view logic from notification creation |
| **Custom Authentication Backend** | `UserManagement/backends.py` | Email-based login instead of username |
| **Custom Middleware** | `MultiAppSessionMiddleware` | Per-role session management |
| **Custom Manager** | `CustomUserManager` | Email normalization on user creation |
| **Custom Template Tags** | `Customer/templatetags/` | `get_item` dict filter, `add_error_class` |
| **Shared Task (Celery)** | `@shared_task` decorator | Tasks work without direct app reference |
| **App Config ready()** | `CustomerConfig`, `SupplierConfig` | Ensures receivers are imported at startup |

---

## Architectural Weaknesses

| Weakness | Impact |
|---|---|
| No service layer | Business logic coupled tightly to views; hard to test or reuse |
| No API layer | Cannot support mobile app or third-party integration without major refactor |
| Duplicate app code | Customer and Supplier share very similar code (registration, email tasks, location model, utils) |
| No caching layer | All page views hit the database directly; no cache headers or query caching |
| SQLite in dev with PostgreSQL in prod | Risk of schema/behavior differences caught only in production |
