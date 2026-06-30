# 10 — Authentication & Authorization

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [05-system-architecture.md](05-system-architecture.md) · [15-security-analysis.md](15-security-analysis.md) · [07-module-analysis.md](07-module-analysis.md)

---

## Authentication Overview

The system uses **email + password authentication** with a custom Django authentication backend. There is no OTP, social login, or multi-factor authentication.

---

## Custom User Model

```python
# UserManagement/models.py
class CustomUser(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'      # Login identifier
    REQUIRED_FIELDS = ['first_name', 'last_name']
```

Key design decisions:
- Email replaces username as the login field
- `user_type` field (`customer`/`supplier`/`admin`) determines role
- All roles share one model — role is self-declared at registration, not enforced by groups

---

## Authentication Backend

```python
# UserManagement/backends.py — EmailBackend
def authenticate(self, request, email=None, password=None, **kwargs):
    user = UserModel.objects.get(email=email)
    if user.check_password(password):
        return user
```

Registered in `settings.py`:
```python
AUTHENTICATION_BACKENDS = [
    'UserManagement.backends.EmailBackend',         # Primary: email-based
    'django.contrib.auth.backends.ModelBackend',    # Fallback: username-based
]
```

---

## Login Flow — Customer

```
POST /Customer/Login/
  ├── email = request.POST.get('email')
  ├── password = request.POST.get('id_passwords')   ← Note unusual POST key name
  ├── user = authenticate(request, email, password)
  ├── if user is not None AND user.user_type == 'customer':
  │     login(request, user)  → sets session
  │     redirect to 'home'
  └── else:
        messages.error('Invalid email or password.')
        redirect to 'login'
```

**Note:** The password POST key is `'id_passwords'` (not `'password'`). This must match the form field `id` attribute in the login template.

---

## Login Flow — Supplier

```
POST /Supplier/Login/
  ├── email = request.POST.get('email')
  ├── password = request.POST.get('password')
  ├── user = authenticate(request, email, password)
  ├── if user is not None AND isinstance(user, CustomUser):   ← ⚠️ MISSING role check
  │     login(request, user)
  │     redirect to 'Home'
  └── else:
        messages.error('Invalid email or password')
        render Login.html
```

**Security Bug:** The condition `isinstance(user, CustomUser)` is always True for any authenticated user. A customer can log into the supplier portal using their customer credentials.

---

## Session Management

### Custom Multi-App Session Middleware

`Water_Tanker_Project/middleware/session_override.py` provides **separate sessions per role**:

```
Path starts with /Supplier/ →
  cookie name: 'supplier_sessionid'
  backend:     django.contrib.sessions.backends.cache (Redis)

Path starts with /Customer/ →
  cookie name: 'customer_sessionid'
  backend:     django.contrib.sessions.backends.db (SQLite/PostgreSQL)

All other paths →
  cookie name: 'sessionid' (default)
  backend:     django.contrib.sessions.backends.db
```

### Session Cookie Properties

Set by the middleware on save:
```python
response.set_cookie(
    key=session_key,
    value=request.session.session_key,
    max_age=60 * 60 * 24,   # 24 hours
    path='/',
    httponly=True,           # ✅ Cannot be read by JavaScript
    samesite='Lax',          # ✅ CSRF protection for same-site requests
)
```

**Inconsistency:** `SESSION_COOKIE_AGE = 3600` (1 hour in settings) vs `max_age = 86400` (24 hours set by middleware). The middleware overrides the Django setting — sessions actually last 24 hours.

**Missing:** `secure=True` is not set — cookies travel over HTTP, not just HTTPS.

---

## Route Protection

### Customer Views
Most views use `@login_required(login_url="login")`:
```python
@login_required(login_url="login")
def home(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'customer') and user.user_type == 'customer':
        return render(request,'home.html')
    else:
        return redirect('login')
```

Pattern: `@login_required` + explicit `user_type` check inside the view body.

### Supplier Views
Most views use `@login_required(login_url="Login_page")`:
```python
@login_required(login_url="Login_page")
def Supp_Home(request):
    if request.user.is_authenticated and request.user.user_type == 'supplier':
        ...
    else:
        messages.error(...)
        return render(request, "Login.html")
```

Pattern: `@login_required` + explicit `user_type` check inside the view body.

### Views Missing Authentication

| View | App | Issue |
|---|---|---|
| `cancel_order` | Customer | No `@login_required` decorator (relies on `get_object_or_404` user filter) |
| `delete_notification` (Supplier) | Supplier | No `@login_required` decorator |

---

## Password Management

### Password Hashing
Registration uses `make_password()`:
```python
# Customer/views.py + Supplier/views.py
user.password = make_password(user_form.cleaned_data['password'])
```

Django's default password hasher (PBKDF2 with SHA256) is used.

### Password Reset Flow
Customer-only feature:

```
1. Customer submits email at POST /Customer/forgot-password/
2. System generates: token = str(uuid.uuid4())
3. Token stored: CustomerProfile.forgot_password_token = token
4. Email sent: http://127.0.0.1:8000/Customer/reset-password/{token}/  ← Hardcoded!
5. Customer clicks link → GET /Customer/reset-password/{token}/
6. Customer submits new password → POST /Customer/reset-password/{token}/
7. System: user.set_password(new_password) + profile.forgot_password_token = None
```

**Issues:**
- Reset URL hardcoded to localhost (production will send wrong link)
- No token expiry (token is valid forever until used)
- No rate limiting on token generation
- No limit on simultaneous reset tokens (each request generates a new one)

---

## Authorization Model

### Role-Based Access

| Role | Identified By | Portals Accessible |
|---|---|---|
| Customer | `user.user_type == 'customer'` | `/Customer/*` |
| Supplier | `user.user_type == 'supplier'` | `/Supplier/*` |
| Admin | `user.is_staff == True` | `/admin/*` |

### Supplier Capability Gates

Suppliers have additional in-app authorization:
1. **Document verification gate:** Cannot go available until `WaterTankerDocument.is_approved == 'Approved'`
2. **Availability gate:** Cannot see/accept orders unless `SupplierProfile.is_available == True`
3. **Order ownership gate:** Order status updates check that the acting driver is assigned to the order (implicit via `driver=driver_detail` filter on queries)

---

## Django Admin Access

```python
# UserManagement/admin.py
class CustomUserAdmin(UserAdmin):
    # Accessible to is_staff=True users
    # is_superuser=True for full permissions
```

Admin can:
- View/edit all CustomUser records
- Filter by user_type, is_staff, is_active
- Search by email
- Approve/reject `WaterTankerDocument` records (if registered in admin)

---

## Authentication Configuration Summary

```python
# settings.py
AUTH_USER_MODEL = 'UserManagement.CustomUser'
AUTHENTICATION_BACKENDS = [
    'UserManagement.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend'
]
LOGIN_URL = '/login/'              # Redirects unauthenticated users
LOGIN_REDIRECT_URL = '/dashboard/' # Default redirect after login (not used — views redirect manually)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600          # Overridden by middleware to 86400
SESSION_COOKIE_SECURE = False      # ⚠️ Should be True in production
```

---

## Summary of Authentication Issues

| Issue | Severity | Details |
|---|---|---|
| Supplier login missing role check | High | Customer can access supplier portal |
| `SESSION_COOKIE_SECURE = False` | Medium | Sessions vulnerable to man-in-the-middle over HTTP |
| Password reset URL hardcoded | High | Production resets send localhost URL |
| No token expiry | Medium | Reset tokens valid forever |
| Missing `@login_required` on cancel_order | Low | Relies on queryset filter as implicit authorization |
| Session age inconsistency (1h vs 24h) | Low | Middleware overrides settings value |
