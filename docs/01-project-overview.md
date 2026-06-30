# 01 — Project Overview

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [02-business-requirements.md](02-business-requirements.md) · [05-system-architecture.md](05-system-architecture.md) · [11-user-flow.md](11-user-flow.md)

---

## Project Identity

| Attribute | Value |
|---|---|
| **Project Name** | Water Tanker Project |
| **Framework** | Django 4.2.7 |
| **Language** | Python 3.11 |
| **Database (dev)** | SQLite (`db.sqlite3`) |
| **Database (prod target)** | PostgreSQL (config present, commented out) |
| **Architecture** | Django MVT (Model-View-Template) |
| **Deployment** | Docker (multi-stage) + Gunicorn + WhiteNoise |
| **Async** | Celery 5 + Redis |
| **Timezone** | Asia/Kolkata (IST) |
| **Locale** | India (INR pricing, Aadhar/PAN docs, Gmail-only email) |

---

## Business Purpose

This is an **on-demand water tanker booking platform** designed for urban India. It solves the problem of the traditional, inefficient phone-based process of arranging water delivery.

The platform connects:
- **Customers** who need water delivered to a specific address
- **Suppliers** (tanker drivers/operators) who fulfill those deliveries
- **Admin** who verifies supplier credentials before they go live

### Core Value Propositions
1. Customers can book a water tanker online in minutes with upfront pricing.
2. Suppliers see orders near them (same pincode) and can accept/manage delivery status.
3. Admin can verify driver documents before any supplier goes live, ensuring safety.
4. Both parties receive in-app notifications at every order status change.

---

## High-Level Feature Summary

### Customer Features
| Feature | Implemented |
|---|---|
| Registration (name, phone, Gmail, password, address) | ✅ |
| Email/password login | ✅ |
| Water tanker booking (capacity + water type) | ✅ |
| Fixed upfront pricing | ✅ |
| Order cancellation (Pending/Accepted only) | ✅ |
| Order status tracking (Driver Detail page) | ✅ |
| In-app notifications from supplier | ✅ |
| Forgot password via email token | ✅ |
| Profile image upload | ✅ |
| Registration confirmation email (async) | ✅ |
| Payment processing | ❌ (model exists, no flow) |
| Real-time push notifications | ❌ (pull-based only) |

### Supplier Features
| Feature | Implemented |
|---|---|
| Registration with auto-created Driver records | ✅ |
| Document upload (7 types) | ✅ |
| Document approval workflow (via admin) | ✅ |
| Availability toggle (post-approval only) | ✅ |
| Dashboard: pending orders in same pincode | ✅ |
| Order accept / cancel | ✅ |
| Order status: On the Way / Delivered | ✅ |
| Earnings: today + 7-day breakdown | ✅ |
| In-app notifications from customer | ✅ |
| Profile page with tanker/document details | ✅ |
| Profile image upload | ✅ |
| Rating system | ❌ (hardcoded "4.5" in profile view) |

### Admin Features
| Feature | Implemented |
|---|---|
| CustomUser management via Django Admin | ✅ |
| Supplier document approval | ✅ (via `WaterTankerDocument.is_approved` field) |
| Order management via admin | Unknown — not explicitly configured |

---

## Technology Stack

```
┌──────────────────────────────────────────────┐
│  Frontend       Bootstrap 5.3 + Bootstrap Icons│
│                 FontAwesome 6.5               │
│                 Inter font (Google Fonts)     │
│                 Vanilla JS (no framework)     │
├──────────────────────────────────────────────┤
│  Backend        Django 4.2.7 (MVT)            │
│                 Custom EmailBackend           │
│                 Custom Session Middleware     │
│                 Django Signals + Receivers    │
├──────────────────────────────────────────────┤
│  Async          Celery 5.5.3                  │
│                 Redis 7 (broker + backend)    │
│                 Celery Beat (scheduled tasks) │
├──────────────────────────────────────────────┤
│  Database       SQLite (dev)                  │
│                 PostgreSQL (prod — disabled)  │
├──────────────────────────────────────────────┤
│  Deployment     Docker (multi-stage build)    │
│                 Gunicorn (3 workers)          │
│                 WhiteNoise (static files)     │
│                 Heroku Procfile present       │
├──────────────────────────────────────────────┤
│  Email          Gmail SMTP (TLS, port 587)    │
│                 python-decouple (.env)        │
└──────────────────────────────────────────────┘
```

---

## Project Context

- The project targets **Indian cities** — pricing in INR, documents are Indian (Aadhar, PAN), only Gmail addresses accepted.
- The platform is a **closed marketplace** — suppliers must be verified before they can operate.
- Current state is an **MVP** — core booking, delivery tracking, and earnings are working; payment processing and real-time push notifications are not yet implemented.
- The codebase is **actively developed** (last commits Dec 2025 – Jun 2026) with ongoing template and migration changes.

---

## Assumptions

> Items marked as assumptions have not been explicitly confirmed in code but are inferred from evidence.

- The platform is intended for a single city/region initially (no multi-region support detected).
- "Supplier" and "Driver" are the same person — a single human who owns and drives the tanker.
- The admin document approval process is manual (no automated workflow or email notification to supplier on approval).
- GPS/real-time location tracking is not implemented despite `latitude`/`longitude` fields existing on `LocationDetail`.
