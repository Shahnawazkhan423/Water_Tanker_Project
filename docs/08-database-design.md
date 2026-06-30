# 08 — Database Design

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [07-module-analysis.md](07-module-analysis.md) · [12-data-flow.md](12-data-flow.md) · [17-improvement-suggestions.md](17-improvement-suggestions.md)

---

## Database Configuration

| Environment | Engine | Location |
|---|---|---|
| Development | SQLite | `BASE_DIR / 'db.sqlite3'` |
| Production (target) | PostgreSQL | Config in `.env` (commented out in `settings.py`) |

**Note:** The production switch requires uncommenting the PostgreSQL `DATABASES` block in `settings.py`.

---

## Entity Relationship Diagram

```
┌─────────────────────────────────┐
│         CustomUser              │ ← UserManagement app
│  PK  id                         │
│      email (unique)             │
│      first_name                 │
│      last_name                  │
│      phone_number               │
│      user_type (customer/       │
│                 supplier/admin) │
│      profile_image              │
│      is_active                  │
│      is_staff                   │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────────────┐
    │          │                  │
    │ 1:1      │ 1:1              │ 1:N
    ▼          ▼                  ▼
┌──────────┐ ┌────────────┐ ┌────────────────┐
│Customer  │ │SupplierP.  │ │DriverAvail-    │
│Profile   │ │            │ │ability         │
│user(1:1) │ │user(1:1)   │ │user (FK)       │
│email     │ │email       │ │availability_dt │
│token     │ │is_available│ │start_time      │
│create_at │ │created_at  │ │end_time        │
│location  │ │location    │ │status          │
│  (FK)    │ │  (FK)      │ └───────┬────────┘
└────┬─────┘ └─────┬──────┘         │ 1:N
     │             │                │
     │             │         ┌──────▼────────┐
     │             │         │  DriverDetail  │
     │             │         │  user (1:1)    │
     │             │         │  availability  │
     │             │         │    (FK)        │
     │             │         └──────┬─────────┘
     │             │                │ 1:N
     │             │         ┌──────▼─────────────────────┐
     │             │         │        TankerDetail        │
     │             │         │  driver (FK → DriverDetail) │
     │             │         │  document (FK → WaterDoc)  │
     │             │         │  capacity (1000-10000)     │
     │             │         │  category                  │
     │             │         │  available                 │
     │             │         └──────────────────────────┬─┘
     │             │                                    │
     │             │                        ┌───────────▼────────────┐
     │             │                        │  WaterTankerDocument   │
     │             │                        │  water_tanker_name     │
     │             │                        │  is_approved           │
     │             │                        │  profile_photo         │
     │             │                        │  driving_license       │
     │             │                        │  aadhar_card           │
     │             │                        │  pan_card              │
     │             │                        │  registration_cert     │
     │             │                        │  vehicle_insurance     │
     │             │                        │  vehicle_permit        │
     │             │                        │  upload_date           │
     │             │                        └────────────────────────┘
     │             │
┌────▼─────────────────────┐        ┌──────────────────────┐
│       OrderDetail        │◄───────│  LocationDetail      │
│  user (FK → CustomUser)  │        │  (Customer app)      │
│  driver (FK → DriverDtl) │        │  address_line        │
│  tanker (FK → TankerDtl) │        │  street              │
│  location (FK → LocDtl)  │        │  landmark            │
│  order_date              │        │  city                │
│  order_status            │        │  state               │
│  delivery_date (nullable)│        │  country (="India")  │
│  quantity (liters)       │        │  pincode             │
│  price                   │        │  latitude (nullable) │
└───────────┬──────────────┘        │  longitude (nullable)│
            │ 1:N                   └──────────────────────┘
            ▼
┌───────────────────────────┐       ┌──────────────────────┐
│         Payment           │       │  LocationDetail       │
│  order (FK)               │       │  (Supplier app)      │
│  amount                   │       │  [same fields]        │
│  payment_method           │       └──────────────────────┘
│  payment_status           │
│  payment_date             │
│  transaction_id           │
└───────────────────────────┘

┌──────────────────────────────────────┐
│           Notification               │
│  customer (FK → CustomUser)          │
│  supplier (FK → SupplierProfile)     │
│  message                             │
│  is_read (default False)             │
│  initiated_by ('customer'/'supplier')│
│  timestamp                           │
└──────────────────────────────────────┘
```

---

## Table Reference

### `auth_user` → `usermanagement_customuser`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `email` | EmailField | UNIQUE | USERNAME_FIELD |
| `first_name` | CharField(30) | NOT NULL | |
| `last_name` | CharField(30) | NOT NULL | |
| `phone_number` | CharField(15) | | |
| `user_type` | CharField(10) | NOT NULL | customer/supplier/admin |
| `profile_image` | ImageField | NULL | Default image path |
| `is_active` | BooleanField | NOT NULL | Default True |
| `is_staff` | BooleanField | NOT NULL | Default False |
| `password` | CharField | NOT NULL | Django password hash |
| `last_login` | DateTimeField | NULL | |

---

### `customer_customerprofile`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user_id` | BigInt | FK → customuser, UNIQUE | OneToOne |
| `email` | EmailField | UNIQUE | Synced from user.email |
| `forgot_password_token` | CharField(100) | | UUID v4 |
| `create_at` | DateTimeField | NOT NULL | auto_now_add |
| `location_id` | BigInt | FK → customer_locationdetail | |

---

### `customer_locationdetail`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `address_line` | CharField(255) | NOT NULL | |
| `street` | CharField(255) | NOT NULL | |
| `landmark` | CharField(255) | NULL | |
| `city` | CharField(255) | NOT NULL | |
| `state` | CharField(255) | NOT NULL | |
| `country` | CharField(255) | NOT NULL | Default "India" |
| `pincode` | CharField(6) | NULL | Used for order matching |
| `latitude` | FloatField | NULL | Not used for matching |
| `longitude` | FloatField | NULL | Not used for matching |

---

### `customer_orderdetail`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user_id` | BigInt | FK → customuser | The customer |
| `driver_id` | BigInt | FK → supplier_driverdetail, NULL | Assigned on accept |
| `tanker_id` | BigInt | FK → supplier_tankerdetail, NULL | Set at booking |
| `location_id` | BigInt | FK → customer_locationdetail | Delivery address |
| `order_date` | DateTimeField | NOT NULL | auto_now_add |
| `order_status` | CharField(20) | NOT NULL | Pending/Accepted/On the Way/Delivered/Canceled |
| `delivery_date` | DateTimeField | NULL | **Never populated** |
| `quantity` | PositiveIntegerField | NOT NULL | Liters |
| `price` | DecimalField(10,2) | NULL | Default 0 |

---

### `customer_payment`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `order_id` | BigInt | FK → customer_orderdetail | |
| `amount` | DecimalField(10,2) | NOT NULL | |
| `payment_method` | CharField(20) | NOT NULL | credit_card/debit_card/paypal/bank_transfer/cash |
| `payment_status` | CharField(20) | NOT NULL | Same choices as order status |
| `payment_date` | DateTimeField | NOT NULL | auto_now_add |
| `transaction_id` | CharField(255) | NULL | |

**Note:** No Payment records are ever created through application views. This table is always empty.

---

### `customer_notification`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `customer_id` | BigInt | FK → customuser | |
| `supplier_id` | BigInt | FK → supplier_supplierprofile | |
| `message` | TextField | NOT NULL | |
| `is_read` | BooleanField | NOT NULL | Default False — never updated |
| `initiated_by` | CharField(10) | NOT NULL | customer/supplier |
| `timestamp` | DateTimeField | NOT NULL | auto_now_add |

---

### `supplier_supplierprofile`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user_id` | BigInt | FK → customuser, UNIQUE | OneToOne |
| `email` | EmailField | UNIQUE | Synced from user.email |
| `is_available` | BooleanField | NOT NULL | Default False |
| `created_at` | DateTimeField | NOT NULL | auto_now_add |
| `location_id` | BigInt | FK → supplier_locationdetail | |

---

### `supplier_locationdetail`

Same structure as `customer_locationdetail` but a separate table in the `supplier` app.

---

### `supplier_driveravailability`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user_id` | BigInt | FK → customuser | related_name='availabilities' |
| `availability_date` | DateField | NOT NULL | |
| `start_time` | TimeField | NOT NULL | |
| `end_time` | TimeField | NULL | Set when going unavailable |
| `status` | CharField(20) | NOT NULL | available/unavailable |
| `notes` | CharField(255) | NULL | |

---

### `supplier_driverdetail`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user_id` | BigInt | FK → customuser, UNIQUE | OneToOne |
| `availability_id` | BigInt | FK → supplier_driveravailability | |

---

### `supplier_watertankerdocument`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `water_tanker_name` | CharField(100) | NOT NULL | |
| `is_approved` | CharField(10) | NOT NULL | Pending/Approved/Rejected |
| `profile_photo` | ImageField | NULL | |
| `driving_license` | FileField | NULL | |
| `aadhar_card` | FileField | NULL | |
| `pan_card` | FileField | NULL | |
| `registration_cert` | FileField | NULL | |
| `vehicle_insurance` | FileField | NULL | |
| `vehicle_permit` | FileField | NULL | |
| `upload_date` | DateTimeField | NOT NULL | auto_now_add |

---

### `supplier_tankerdetail`

| Column | Type | Constraint | Notes |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `driver_id` | BigInt | FK → supplier_driverdetail, NULL | |
| `document_id` | BigInt | FK → supplier_watertankerdocument, NULL | |
| `capacity` | PositiveIntegerField | NOT NULL | 1000/2000/5000/10000 |
| `category` | CharField(20) | NOT NULL | DRINKING/NON_DRINKING/BOTH |
| `available` | BooleanField | NOT NULL | Default True |

---

## Key Relationships Summary

| Relationship | Type | Notes |
|---|---|---|
| CustomUser ↔ CustomerProfile | OneToOne | `customer` related_name |
| CustomUser ↔ SupplierProfile | OneToOne | `supplier` related_name |
| CustomUser ↔ DriverDetail | OneToOne | |
| CustomUser → DriverAvailability | ForeignKey (1:N) | `availabilities` related_name |
| CustomerProfile → LocationDetail | ForeignKey | Customer registration address |
| SupplierProfile → LocationDetail | ForeignKey | Supplier operating area |
| OrderDetail → CustomUser | ForeignKey | Customer who placed order |
| OrderDetail → DriverDetail | ForeignKey (nullable) | Assigned supplier/driver |
| OrderDetail → TankerDetail | ForeignKey (nullable) | Tanker used for delivery |
| OrderDetail → LocationDetail | ForeignKey | Delivery address |
| Payment → OrderDetail | ForeignKey (1:N) | Multiple payments per order possible |
| Notification → CustomUser | ForeignKey | Customer side |
| Notification → SupplierProfile | ForeignKey | Supplier side |
| TankerDetail → DriverDetail | ForeignKey | Driver who owns tanker |
| TankerDetail → WaterTankerDocument | ForeignKey | Verification documents |

---

## Design Issues

| Issue | Impact |
|---|---|
| `LocationDetail` duplicated in Customer + Supplier apps | Two separate tables; no cross-join possible; violates DRY |
| `OrderDetail.delivery_date` never populated | Useless field consuming space |
| `OrderDetail.tanker` is a new `TankerDetail` per booking, not supplier's tanker | Orders are disconnected from real supplier inventory |
| `CustomerProfile.forgot_password_token` has no expiry datetime | Security vulnerability |
| `Notification.is_read` never set to True | Field is dead code |
| `Payment` table always empty | Payment feature is incomplete |
| No indexes on `order_status`, `driver`, `location__pincode` | Full table scans on every dashboard/order-list load |
| `Payment.payment_status` uses same choices as `OrderDetail.order_status` | Wrong — Payment status should be Pending/Completed/Failed/Refunded |
