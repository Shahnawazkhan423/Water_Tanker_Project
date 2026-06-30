# 04 — Non-Functional Requirements

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [15-security-analysis.md](15-security-analysis.md) · [16-performance-analysis.md](16-performance-analysis.md) · [17-improvement-suggestions.md](17-improvement-suggestions.md)

---

## NFR-01: Performance

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-01.1 | Registration/login response time < 500ms | Partially met | Synchronous DB calls; email is async via Celery |
| NFR-01.2 | Booking form submission < 1s | At risk | `transaction.atomic()` wraps 3 DB writes; SQLite has no concurrency |
| NFR-01.3 | Dashboard data loads in < 1s | At risk | Multiple unindexed queries on `OrderDetail` |
| NFR-01.4 | Email sending must not block user responses | ✅ Met | `send_email_task.delay()` (Celery async) |
| NFR-01.5 | Page loads should not trigger N+1 queries | Partially met | `select_related` used in supplier order views; missing elsewhere |
| NFR-01.6 | Order/notification lists should be paginated | ❌ Not met | No pagination anywhere |

---

## NFR-02: Security

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-02.1 | All passwords must be hashed | ✅ Met | `make_password()` / `set_password()` used |
| NFR-02.2 | All forms must be CSRF-protected | ❌ Not met | Most views use `@csrf_exempt` |
| NFR-02.3 | Session cookies must be HTTPOnly | ✅ Met | `httponly=True` in `MultiAppSessionMiddleware` |
| NFR-02.4 | Session cookies must be Secure (HTTPS-only) | ❌ Not met | `SESSION_COOKIE_SECURE = False` |
| NFR-02.5 | Secrets must not be in version control | ❌ Not met | `.env` is committed to git |
| NFR-02.6 | Password reset tokens must expire | ❌ Not met | Tokens never expire |
| NFR-02.7 | Input validation on both client and server | ✅ Met | HTML5 `pattern` + Django `clean_*` methods |
| NFR-02.8 | Role-based access must be enforced | Partially met | Customer views OK; Supplier login missing role check |
| NFR-02.9 | File uploads must be type-validated | ✅ Met | `WaterTankerForm._clean_file_field()` |
| NFR-02.10 | Debug mode must be off in production | ❌ Not met | `DEBUG=True` in committed `.env` |

---

## NFR-03: Scalability

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-03.1 | App must support multiple concurrent requests | ✅ Met | Gunicorn with 3 workers |
| NFR-03.2 | Async workloads must scale independently | ✅ Met | Celery workers can be scaled horizontally |
| NFR-03.3 | Database must support concurrent writes | ❌ Not met (dev) | SQLite — single writer; PostgreSQL config exists but disabled |
| NFR-03.4 | Static files must not be served by Django | ✅ Met | WhiteNoise configured for production |
| NFR-03.5 | Order matching must not become a bottleneck as orders grow | At risk | Full table scan on `OrderDetail` filtered by pincode; no index |

---

## NFR-04: Availability & Reliability

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-04.1 | App must restart cleanly via Docker | ✅ Met | Multi-stage Dockerfile with `CMD migrate + collectstatic + gunicorn` |
| NFR-04.2 | Failed email sends must not crash the app | ✅ Met | Celery tasks catch exceptions; `fail_silently` not used but exceptions logged |
| NFR-04.3 | Celery Beat scheduled tasks must fire reliably | ⚠️ At risk | Both beat schedules overwrite each other; only one fires |
| NFR-04.4 | Database migrations must run automatically on deploy | ✅ Met | `python manage.py migrate --noinput` in Docker CMD |

---

## NFR-05: Usability

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-05.1 | Mobile-responsive UI | ✅ Met | Bootstrap 5 + responsive CSS in `_base.html` |
| NFR-05.2 | User feedback for all actions (success/error) | ✅ Met | Django messages → JS toast system |
| NFR-05.3 | Form errors clearly displayed | ✅ Met | `add_error_class` template tag + Bootstrap `is-invalid` |
| NFR-05.4 | Loading states for async actions | ✅ Met | `btn-loading` CSS class + spinner animation defined |
| NFR-05.5 | Consistent design language | ✅ Met | CSS design tokens in `_base.html` (colors, spacing, shadows) |
| NFR-05.6 | Order status clearly visible | ✅ Met | Color-coded status badges (`status-pending`, `status-accepted`, etc.) |

---

## NFR-06: Maintainability

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-06.1 | Clear separation of concerns | ✅ Met | MVT pattern, Signal/Receiver decouples notification logic |
| NFR-06.2 | No code duplication across apps | ❌ Not met | `send_email_task`, `haversine_distance`, `LocationDetail`, `send_mail_every_day` duplicated |
| NFR-06.3 | Configuration from environment variables | ✅ Met | `python-decouple` reads from `.env` |
| NFR-06.4 | Tests exist | ❌ Not met | Test files exist (`Customer/tests.py`, etc.) but are empty stubs |
| NFR-06.5 | No debug print statements in production | ❌ Not met | Multiple `print()` calls in `Customer/views.py` |
| NFR-06.6 | Dependency list is clean (no unused packages) | ❌ Not met | crispy-forms, DRF, model-utils, dotenv, mysqlclient unused |

---

## NFR-07: Internationalization

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-07.1 | Application is localized for India | ✅ Met | `TIME_ZONE='Asia/Kolkata'`, INR pricing, Indian documents |
| NFR-07.2 | Multi-language support | ❌ Not implemented | `USE_I18N=True` set but no translation files |
| NFR-07.3 | Date/time displayed in IST | ✅ Met | `CELERY_TIMEZONE='Asia/Kolkata'`, `localtime()` used in earning view |

---

## NFR-08: Deployment

| ID | Requirement | Current Status | Evidence |
|---|---|---|---|
| NFR-08.1 | Application can be containerized | ✅ Met | Multi-stage Dockerfile |
| NFR-08.2 | Application can be deployed to Heroku | ✅ Met | `Procfile` present |
| NFR-08.3 | Application runs as non-root user in container | ✅ Met | Dockerfile creates `appuser` |
| NFR-08.4 | Static files collected at build time | ✅ Met | `collectstatic --noinput --clear` in CMD |
| NFR-08.5 | Application supports PostgreSQL in production | ⚠️ Partially met | Config present but commented out; PostgreSQL driver installed |
| NFR-08.6 | Redis must be separately provisioned | Not automated | No Redis in Dockerfile; must be provided externally |

---

## Summary Table

| Category | Requirements | Met | Partially Met | Not Met |
|---|---|---|---|---|
| Performance | 6 | 1 | 3 | 2 |
| Security | 10 | 4 | 2 | 4 |
| Scalability | 5 | 3 | 1 | 1 |
| Availability | 4 | 3 | 1 | 0 |
| Usability | 6 | 6 | 0 | 0 |
| Maintainability | 6 | 2 | 0 | 4 |
| I18n | 3 | 2 | 0 | 1 |
| Deployment | 6 | 4 | 2 | 0 |
| **Total** | **46** | **25 (54%)** | **9 (20%)** | **12 (26%)** |
