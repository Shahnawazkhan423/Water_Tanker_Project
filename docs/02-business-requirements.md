# 02 — Business Requirements

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [01-project-overview.md](01-project-overview.md) · [03-functional-requirements.md](03-functional-requirements.md) · [11-user-flow.md](11-user-flow.md)

---

## Business Context

Water delivery via tankers is a daily necessity in many Indian cities where piped water supply is insufficient or unreliable. The traditional process relies on phone calls, personal contacts, and informal negotiations — leading to:

- **No price transparency** — customers don't know the cost upfront
- **No delivery tracking** — customers wait without knowing ETA
- **No driver vetting** — customers have no way to verify the driver
- **No digital record** — no order history, no receipts, no dispute resolution

This platform addresses all four pain points digitally.

---

## Stakeholders

| Stakeholder | Role | Needs |
|---|---|---|
| **Customer** | Books water for home/business | Easy booking, fair price, status tracking, reliable delivery |
| **Supplier (Driver)** | Delivers water, earns income | Order discovery in their area, clear status workflow, earnings tracking |
| **Platform Admin** | Operates the platform | Verified suppliers, fraud prevention, document compliance |
| **Tanker Owner** | (May differ from driver) | Currently not modeled separately — assumed same as Supplier |

---

## Business Rules (Derived from Implementation)

### Pricing Rules
| Capacity | Price per Liter | Total Price |
|---|---|---|
| 1,000 L | ₹0.15/L | ₹150 |
| 2,000 L | ₹0.12/L | ₹240 |
| 5,000 L | ₹0.10/L | ₹500 |
| 10,000 L | ₹0.08/L | ₹800 |

- Prices are **fixed** (bulk discount for larger orders).
- Pricing is calculated at booking time and stored in `OrderDetail.price`.
- The `TankerDetail.price_per_liter` property and `calculate_price()` method exist but the booking view uses its own inline pricing dict — these are **inconsistently defined in two places**.

### Supplier Eligibility Rules
1. A supplier must upload all 7 required documents during registration.
2. Documents must receive Admin approval (`WaterTankerDocument.is_approved = 'Approved'`) before the supplier can toggle availability.
3. Only available suppliers appear as candidates for pending orders.

### Order Matching Rules
- A supplier sees pending orders **only in their own pincode** (`supplier.location.pincode == order.location.pincode`).
- There is **no distance-based matching** despite `latitude`/`longitude` fields and `geopy`/`haversine` utilities being present.
- Only one supplier can accept a given order (first-accept-wins; no bidding).

### Order State Machine

```
             ┌─────────┐
             │ PENDING │ ◄── Created on customer booking
             └────┬────┘
          ┌───────┴────────┐
          │                │
     [Supplier         [Supplier
      accepts]          cancels]
          │                │
          ▼                ▼
     ┌──────────┐     ┌──────────┐
     │ ACCEPTED │     │ CANCELED │
     └────┬─────┘     └──────────┘
     │         │
[Customer  [Supplier
 cancels]  "On the Way"]
     │         │
     ▼         ▼
┌──────────┐  ┌────────────┐
│ CANCELED │  │ ON THE WAY │
└──────────┘  └─────┬──────┘
                    │
             [Supplier "Delivered"]
                    │
                    ▼
              ┌───────────┐
              │ DELIVERED │
              └───────────┘
```

**Rules:**
- Customer can cancel only when status is `Pending` or `Accepted`.
- Once `On the Way` or `Delivered`, the order cannot be cancelled by the customer.
- Supplier can cancel only from `Pending` status (via the accept/cancel action route).
- Status transitions: `Pending → Accepted → On the Way → Delivered` (happy path).

### Email Communication Rules
- Registration email sent to new users (Customer and Supplier) — async via Celery.
- Daily "Good Evening" email sent to **all users** at 19:00 IST via Celery Beat.
- Password reset email sent via synchronous `send_mail` call (not async).

### Notification Rules
| Event | Who Gets Notified | `initiated_by` |
|---|---|---|
| Customer cancels order | Supplier | `'customer'` |
| Supplier accepts order | Customer | `'supplier'` |
| Supplier marks "On the Way" | Customer | `'supplier'` |
| Supplier marks "Delivered" | Customer | `'supplier'` |
| Supplier cancels order | Customer | `'supplier'` |

- Notifications are stored in the database and displayed on a dedicated notifications page.
- There is no badge count or unread indicator implemented beyond the `is_read` boolean field (which is never set to `True` in any view).

### Authentication Rules
- Login is by **email + password only** (no OTP, no social login).
- Email must be a **Gmail address** (`@gmail.com` pattern enforced in form validation).
- Customer and Supplier have **separate login pages** and **separate session cookies**.
- A supplier logging into the customer portal (or vice versa) produces an error.

---

## Business Metrics (Supported by Implementation)

| Metric | How Captured |
|---|---|
| Orders accepted | `OrderDetail.objects.filter(order_status='Accepted', driver=driver).count()` |
| Orders completed | `OrderDetail.objects.filter(order_status='Delivered', driver=driver).count()` |
| Revenue today | `Sum('price')` on delivered orders from last 24h |
| Revenue last 7 days | Per-day sum in a loop (last 7 calendar days) |
| Total revenue | Sum of all per-day revenue over 7 days |

**Not tracked:** customer lifetime value, platform-level revenue (no commission model visible), cancellation rate, average delivery time.

---

## Business Constraints

| Constraint | Evidence |
|---|---|
| India only | Default country "India", pricing in ₹, Indian documents required |
| Gmail only | Form regex enforces `@gmail.com` |
| 4 fixed tanker sizes | `CAPACITY_CHOICES` on `TankerDetail` |
| 3 water categories | `CATEGORY_CHOICES`: Drinking, Non-Drinking, Both |
| Manual admin approval | No automated approval or rejection logic |
| No payment gateway | `Payment` model exists but no payment processing is implemented |

---

## Open Questions

| # | Question | Source |
|---|---|---|
| Q1 | Is there a commission model? (Platform takes % per order?) | Not found in codebase |
| Q2 | Who approves supplier documents — a dedicated admin team or the platform owner? | Unknown |
| Q3 | Can a supplier own multiple tankers? (TankerDetail → DriverDetail is FK, not M2M) | Partially — one `DriverDetail` can have multiple `TankerDetail` rows |
| Q4 | Is "Supplier" always the same person as the driver, or can a company register? | Assumed same person based on model design |
| Q5 | What happens if no supplier is available in the customer's pincode? | Order sits in Pending indefinitely — no timeout or fallback |
| Q6 | Is the rating system (hardcoded "4.5" in supplier profile) planned? | Unknown |
