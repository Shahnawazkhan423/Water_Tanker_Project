# 14 — Third-Party Dependencies

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [05-system-architecture.md](05-system-architecture.md) · [16-performance-analysis.md](16-performance-analysis.md) · [17-improvement-suggestions.md](17-improvement-suggestions.md)

---

## Python Packages (`requirements.txt`)

### Core Framework

| Package | Version | Used | Purpose |
|---|---|---|---|
| **Django** | 4.2.7 | ✅ Yes | Web framework — MVT, ORM, auth, admin, sessions |
| **asgiref** | 3.8.1 | ✅ Yes | Django async support (ASGI compatibility) |
| **sqlparse** | 0.5.3 | ✅ Yes | Django dependency for SQL formatting in debug |

> **Note:** `settings.py` header says "Generated using Django 5.1.7" but `requirements.txt` pins Django 4.2.7. The actual running version is **4.2.7 (LTS)**.

---

### Async Task Queue

| Package | Version | Used | Purpose |
|---|---|---|---|
| **celery** | 5.5.3 | ✅ Yes | Async task queue (email sending, scheduled tasks) |
| **redis** | 7.0.1 | ✅ Yes | Python Redis client — Celery broker + result backend |
| **kombu** | 5.5.4 | ✅ Yes | Celery dependency — messaging library |
| **billiard** | 4.2.3 | ✅ Yes | Celery dependency — multiprocessing |
| **amqp** | 5.3.1 | ✅ Yes | Celery dependency — AMQP protocol |
| **vine** | 5.1.0 | ✅ Yes | Celery dependency — promise/callback utilities |
| **click** | 8.3.1 | ✅ Yes | Celery CLI dependency |
| **click-didyoumean** | 0.3.1 | ✅ Yes | Celery CLI |
| **click-plugins** | 1.1.1.2 | ✅ Yes | Celery CLI |
| **click-repl** | 0.3.0 | ✅ Yes | Celery CLI REPL |
| **prompt_toolkit** | 3.0.52 | ✅ Yes | Celery CLI terminal input |
| **wcwidth** | 0.2.14 | ✅ Yes | Terminal width calculation |

---

### Configuration & Environment

| Package | Version | Used | Purpose |
|---|---|---|---|
| **python-decouple** | 3.8 | ✅ Yes | Reads `.env` file with `config()` calls in `settings.py` |
| **python-dotenv** | 1.0.0 | ⚠️ Redundant | Also reads `.env` — overlaps with python-decouple; not used directly |

> **Recommendation:** Remove `python-dotenv` — `python-decouple` fully covers this use case.

---

### Database Drivers

| Package | Version | Used | Purpose |
|---|---|---|---|
| **psycopg2-binary** | 2.9.10 | ⚠️ Inactive | PostgreSQL driver — installed but DB config is commented out |
| **mysqlclient** | 2.2.1 | ⚠️ Likely unused | MySQL driver — no MySQL config found; Dockerfile installs MySQL client |
| **dj-database-url** | 3.0.1 | ⚠️ Inactive | Parse DATABASE_URL env var — imported in settings but not called |

> **Note on MySQL:** The Dockerfile installs `default-mysql-client` and `libmariadb3`, and `mysqlclient` is in requirements. This suggests MySQL was considered at some point. Current dev uses SQLite; PostgreSQL is the intended production DB.

> **Recommendation:** Remove `mysqlclient` and `dj-database-url` unless MySQL or a DATABASE_URL is actually needed.

---

### Image & File Handling

| Package | Version | Used | Purpose |
|---|---|---|---|
| **Pillow** | 10.4.0 | ✅ Yes | `ImageField` support in Django — profile images, tanker photos |

---

### Geolocation

| Package | Version | Used | Purpose |
|---|---|---|---|
| **geopy** | 2.4.1 | ⚠️ Imported but unused | `from geopy.distance import geodesic` imported in both view files but never called |
| **geographiclib** | 2.0 | ⚠️ Indirect | geopy dependency |

> **Note:** `haversine_distance()` is manually reimplemented in both `Customer/utils.py` and `Supplier/utils.py`. Neither the manual implementation nor `geopy.geodesic` is actually called anywhere in views. Order matching uses pincode equality only.

> **Recommendation:** Either implement geo-distance matching (remove manual haversine, use geopy properly) or remove geopy entirely and use pincode-based matching explicitly.

---

### Production Server & Static Files

| Package | Version | Used | Purpose |
|---|---|---|---|
| **gunicorn** | 21.2.0 | ✅ Yes | WSGI production server (3 workers configured in Dockerfile) |
| **whitenoise** | 6.5.0 | ✅ Yes | Serves static files from Django/Gunicorn without nginx |

> WhiteNoise is not configured in `MIDDLEWARE` in the visible `settings.py`. It may be added via `whitenoise.middleware.WhiteNoiseMiddleware` or by Gunicorn serving the WSGI app — verify this.

---

### Date & Time Utilities

| Package | Version | Used | Purpose |
|---|---|---|---|
| **python-dateutil** | 2.9.0.post0 | ✅ Yes | `relativedelta` used in `Supplier/utils.py: human_readable_joined_date()` |
| **pytz** | 2025.2 | ✅ Yes | Timezone handling (Django also uses `zoneinfo` internally) |
| **tzdata** | 2025.2 | ✅ Yes | Timezone database |
| **six** | 1.17.0 | ✅ Yes | Python 2/3 compat — transitive dependency |
| **packaging** | 25.0 | ✅ Yes | Transitive dependency |
| **typing_extensions** | 4.14.0 | ✅ Yes | Transitive dependency |

---

### Django Extensions (Installed but Unused)

| Package | Version | Used | Purpose in requirements | Actual usage |
|---|---|---|---|---|
| **django-crispy-forms** | 2.1 | ❌ Unused | Better form rendering with layout helpers | Not used in any template |
| **crispy-bootstrap5** | 0.7 | ❌ Unused | Bootstrap 5 template pack for crispy-forms | Not used |
| **djangorestframework** | 3.14.0 | ❌ Unused | REST API framework | Installed, no ViewSets/Serializers defined |
| **django-model-utils** | 5.0.0 | ❌ Unused | `StatusField`, `TimeStampedModel`, etc. | In `INSTALLED_APPS` as `model_utils` but no models extend it |

> **Recommendation:** Remove all four packages. They add ~10MB to the Docker image and create maintenance surface without benefit.

---

## CDN Front-End Dependencies

These are loaded via CDN links in HTML templates — not in `requirements.txt`.

| Library | Version | CDN URL | Purpose |
|---|---|---|---|
| Bootstrap CSS | 5.3.3 | `cdn.jsdelivr.net` | Layout, components, grid |
| Bootstrap JS Bundle | 5.3.3 | `cdn.jsdelivr.net` | Dropdowns, modals, collapse |
| Bootstrap Icons | 1.11.3 | `cdn.jsdelivr.net` | Icon font (bi-* classes) |
| Font Awesome | 6.5.1 | `cdnjs.cloudflare.com` | Additional icons (fas-*, fa-*) |
| Google Fonts — Inter | Latest | `fonts.googleapis.com` | Primary typeface |

**Implication:** The app requires internet access to render correctly. In offline/intranet environments, these CDN assets would fail to load.

---

## Dependency Audit Summary

| Category | Count | Status |
|---|---|---|
| Actively used | 22 | ✅ Keep |
| Celery ecosystem (indirect) | 8 | ✅ Keep (required by celery) |
| Unused / redundant | 7 | ❌ Remove |
| Inactive (driver for future use) | 3 | ⚠️ Decision needed |

### Packages Safe to Remove

```
python-dotenv==1.0.0        # Redundant with python-decouple
django-crispy-forms==2.1    # Never used in templates
crispy-bootstrap5==0.7      # Depends on crispy-forms (also unused)
djangorestframework==3.14.0 # No REST API implemented
django-model-utils==5.0.0   # No models use its features
mysqlclient==2.2.1          # No MySQL config
dj-database-url==3.0.1      # Not called in settings
```

Removing these would slim the Docker image and reduce the dependency attack surface.

---

## Version Risk Assessment

| Package | LTS/Stable | Notes |
|---|---|---|
| Django 4.2.7 | ✅ LTS (supported until April 2026) | Upgrade to 5.x when ready |
| Celery 5.5.3 | ✅ Current | |
| Redis 7.0.1 | ✅ Stable | |
| Pillow 10.4.0 | ✅ Stable | |
| gunicorn 21.2.0 | ✅ Stable | |
| psycopg2-binary 2.9.10 | ✅ Stable | Consider psycopg3 for new projects |

> Django 4.2 LTS end-of-life is April 2026. Plan upgrade to Django 5.x before that date.
