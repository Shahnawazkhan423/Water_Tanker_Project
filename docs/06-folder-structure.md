# 06 — Folder Structure

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [05-system-architecture.md](05-system-architecture.md) · [07-module-analysis.md](07-module-analysis.md)

---

## Root Directory Layout

```
Water_Tanker_Project/
│
├── Water_Tanker_Project/        ← Django project configuration package
├── Customer/                    ← Customer domain app
├── Supplier/                    ← Supplier domain app
├── UserManagement/              ← Shared authentication/user app
├── templates/                   ← Global templates (new — recently added)
├── static/                      ← Source static assets
├── staticfiles/                 ← Collected static assets (production)
├── media/                       ← User-uploaded files
├── docs/                        ← Project documentation (this folder)
├── venv/                        ← Python virtual environment (not committed)
│
├── manage.py                    ← Django management CLI entry point
├── db.sqlite3                   ← SQLite development database
├── requirements.txt             ← Python dependencies
├── Dockerfile                   ← Multi-stage Docker build definition
├── Procfile                     ← Heroku/Railway process declaration
├── celerybeat-schedule          ← Celery Beat runtime schedule store (binary)
├── .env                         ← Environment variables (⚠️ committed to git)
└── .gitignore                   ← Git ignore rules
```

---

## Project Configuration Package (`Water_Tanker_Project/`)

```
Water_Tanker_Project/
├── __init__.py                  ← Imports Celery app to ensure it's loaded at startup
├── settings.py                  ← All configuration (DB, auth, email, Celery, static)
├── urls.py                      ← Root URL dispatcher
├── celery.py                    ← Celery app instance + Beat schedule definition
├── wsgi.py                      ← WSGI entry point (Gunicorn uses this)
├── asgi.py                      ← ASGI entry point (unused — no WebSocket support)
└── middleware/
    ├── __init__.py
    └── session_override.py      ← MultiAppSessionMiddleware (per-role sessions)
```

**Key point:** `Water_Tanker_Project/__init__.py` imports the Celery app instance so it is always available when Django starts.

---

## UserManagement App (`UserManagement/`)

```
UserManagement/
├── __init__.py
├── apps.py                      ← AppConfig (no custom ready() hook)
├── admin.py                     ← CustomUserAdmin — registers CustomUser in admin
├── backends.py                  ← EmailBackend — email-based authentication
├── models.py                    ← CustomUser, CustomUserManager
├── views.py                     ← role_selection — landing page view only
├── urls.py                      ← Empty (no app-level URLs; root urls.py calls views directly)
├── tests.py                     ← Empty stub
├── migrations/
│   └── 0001_initial.py          ← CustomUser table creation
└── templates/
    └── base.html                ← Landing page HTML (role selection/login links)
```

**Purpose:** Shared identity layer. All user types share a single `CustomUser` model. This app has no business logic — just user storage and authentication.

---

## Customer App (`Customer/`)

```
Customer/
├── __init__.py
├── apps.py                      ← CustomerConfig — ready() imports receivers
├── admin.py                     ← Empty (no Customer models registered in admin)
├── models.py                    ← CustomerProfile, LocationDetail, OrderDetail,
│                                     Payment, Notification
├── views.py                     ← All customer views (12 view functions)
├── forms.py                     ← UserDetailForm, BookingUserForm,
│                                     TankerDetailForm, LocationDetailForm
├── urls.py                      ← All /Customer/* URL patterns
├── signals.py                   ← order_canceled_by_customer Signal definition
├── receivers.py                 ← Signal handler → creates supplier Notification
├── tasks.py                     ← Celery: send_email_task, send_mail_every_day
├── helper.py                    ← send_forgot_password_mail() helper function
├── utils.py                     ← haversine_distance() (defined but unused in views)
├── tests.py                     ← Empty stub
├── migrations/
│   ├── 0001_initial.py
│   ├── 0002_initial.py
│   └── 0003_initial.py
├── templates/
│   ├── booking.html
│   ├── driver_detail.html
│   ├── forgot_password.html
│   ├── home.html
│   ├── login.html
│   ├── notification.html
│   ├── profile.html
│   ├── register.html
│   └── reset_passwords.html
└── templatetags/
    ├── __init__.py
    └── custom_filters.py        ← get_item, add_error_class template filters
```

---

## Supplier App (`Supplier/`)

```
Supplier/
├── __init__.py
├── apps.py                      ← SupplierConfig — ready() imports receivers
├── admin.py                     ← (Not read; assumed empty or basic)
├── models.py                    ← LocationDetail, SupplierProfile, DriverAvailability,
│                                     DriverDetail, WaterTankerDocument, TankerDetail
├── views.py                     ← All supplier views (14 view functions)
├── forms.py                     ← SupplierRegistrationForm, SupplierLocationDetailForm,
│                                     SupplierTankerDetailForm, WaterTankerForm
├── urls.py                      ← All /Supplier/* URL patterns
├── signals.py                   ← 4 Signal definitions (accepted/canceled/on_way/delivered)
├── receivers.py                 ← 4 Signal handlers → create customer Notifications
├── tasks.py                     ← Celery: send_email_task, send_mail_every_day (duplicate)
├── utils.py                     ← haversine_distance(), human_readable_joined_date()
├── tests.py                     ← Empty stub
├── migrations/
│   ├── 0001_initial.py
│   └── 0002_initial.py
└── templates/
    ├── Earning.html
    ├── Home.html
    ├── Login.html
    ├── Notification.html
    ├── Order_List.html
    ├── Profile.html
    ├── Register.html
    └── tanker_detail.html
```

---

## Global Templates (`templates/`)

```
templates/
├── _base.html                   ← Master CSS design system + JS utilities
│                                    (design tokens, Bootstrap 5, toast system,
│                                     password toggle, animations, skeleton loaders)
└── _auth.html                   ← Auth layout template (extends _base.html)
```

**Note:** This folder was recently added (`?? templates/` in git status). The `_base.html` is the new shared design system. The app-level `base.html` in `UserManagement/templates/` extends `_base.html`.

---

## Static Assets (`static/`)

```
static/
├── image/                       ← Static images
└── media/                       ← Media files (likely profile image placeholders)
    └── deafult_Profile_Image.jpg  ← Default profile image (note typo in filename)
```

**Note:** `STATICFILES_DIRS = [BASE_DIR / "static"]`. Collected to `staticfiles/` by `collectstatic`.

---

## Media Files (`media/`)

```
media/
├── media/                       ← Uploaded profile images
│   └── deafult_Profile_Image.jpg
└── tanker/
    ├── profile/                 ← Tanker profile photos
    ├── license/                 ← Driving licenses
    ├── aadhar/                  ← Aadhar cards
    ├── pan/                     ← PAN cards
    ├── rc/                      ← Registration certificates
    ├── insurance/               ← Vehicle insurance docs
    └── permit/                  ← Vehicle permits
```

**Note:** `MEDIA_URL = '/media/'`, `MEDIA_ROOT = BASE_DIR / "media"`. Served by `static(MEDIA_URL, ...)` in dev; needs separate handling in production.

---

## File Naming Conventions

| Category | Convention | Example |
|---|---|---|
| Customer templates | `lowercase.html` | `booking.html`, `home.html` |
| Supplier templates | `TitleCase.html` | `Home.html`, `Order_List.html` |
| Customer URL names | `snake_case` | `driver_detail`, `forgot_password` |
| Supplier URL names | Mixed | `Home`, `Order_List`, `Register_page` |
| Python files | Standard Django naming | `models.py`, `views.py` |

**Inconsistency:** Customer templates use lowercase, Supplier templates use TitleCase — this is an inconsistency in the codebase that should be standardized.

---

## What Is Missing from Folder Structure

| Missing Item | Impact |
|---|---|
| `requirements-dev.txt` | No separation of dev vs prod dependencies |
| `.env.example` | No template for new developers to configure their environment |
| Test fixtures | No sample data for testing |
| `docker-compose.yml` | No local orchestration for Django + Redis + Celery |
| `conftest.py` or test structure | No testing infrastructure |
| `nginx.conf` | No reverse proxy configuration for production |
