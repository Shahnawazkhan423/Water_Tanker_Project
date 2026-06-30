# 18 — Development Roadmap

> **Status:** Complete  
> **Last Updated:** 2026-06-30  
> **Cross-references:** [17-improvement-suggestions.md](17-improvement-suggestions.md) · [15-security-analysis.md](15-security-analysis.md) · [03-functional-requirements.md](03-functional-requirements.md)

---

## Current State Assessment

| Category | Score | Notes |
|---|---|---|
| Functional completeness | 7/10 | Core booking/delivery flow works; payment missing |
| Security | 3/10 | Multiple critical and high-severity issues |
| Performance | 5/10 | Async email done; no indexes, no pagination |
| Code quality | 6/10 | Good signal pattern; duplicate code across apps |
| Test coverage | 0/10 | All test files empty |
| Documentation | 9/10 | This documentation set |
| Deployment readiness | 5/10 | Docker ready; DB and secrets not production-safe |

---

## Phase 0 — Pre-Production Hardening (Immediate — 1 Week)

These must be done before any production deployment.

| ID | Task | Effort | Ref |
|---|---|---|---|
| 0.1 | Remove `.env` from git history, rotate all secrets | 2h | S-01 |
| 0.2 | Create `.env.example` | 30min | P-13 |
| 0.3 | Fix password reset URL (use `request.build_absolute_uri`) | 30min | S-02 |
| 0.4 | Fix supplier login role guard (`user_type == 'supplier'`) | 15min | S-03 |
| 0.5 | Fix cancel order `AttributeError` in receiver (`customer_user.name`) | 15min | S-04 |
| 0.6 | Remove `@csrf_exempt` from all non-JSON views | 1h | S-05 |
| 0.7 | Set `DEBUG=False` and `SESSION_COOKIE_SECURE=True` in production | 30min | — |
| 0.8 | Add `@login_required` to `cancel_order` view | 10min | S-10 |
| 0.9 | Remove all `print()` statements, add proper logging | 30min | P-08 |
| 0.10 | Switch to PostgreSQL for dev environment | 2h | E-09 |

**Estimated total effort:** ~1 day

---

## Phase 1 — Bug Fixes & Code Quality (Sprint 1 — Weeks 1-2)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 1.1 | Fix Celery daily email task — move `send_mail()` inside loop | 30min | S-06 |
| 1.2 | Fix Celery beat schedule overwrite — merge into single dict | 15min | S-07 |
| 1.3 | Add password reset token expiry (add `token_created_at` field + view check) | 2h | S-08 |
| 1.4 | Remove 7 unused packages from requirements.txt | 30min | P-07 |
| 1.5 | Consolidate duplicate `send_email_task` into shared task | 1h | P-02 |
| 1.6 | Fix session age inconsistency (use settings value in middleware) | 15min | P-14 |
| 1.7 | Standardize URL names and template file naming conventions | 2h | P-11 |
| 1.8 | Add `docker-compose.yml` for local dev (Django + PostgreSQL + Redis + Celery) | 3h | P-12 |

**Estimated total effort:** ~2 days

---

## Phase 2 — Performance & Database (Sprint 2 — Weeks 3-4)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 2.1 | Add `db_index=True` to `order_status`, `pincode` fields | 30min + migration | P-04 |
| 2.2 | Add pagination to: Customer notifications, Supplier notifications, Supplier order list | 3h | P-05 |
| 2.3 | Optimize Supplier earnings — replace 7 queries with single annotated query | 2h | P-06 |
| 2.4 | Consolidate `LocationDetail` into single shared model | 4h + migration | P-01 |
| 2.5 | Refactor `get_supplier_dashboard_data` as a plain helper function (remove decorators) | 30min | P-06 ref |
| 2.6 | Add `select_related` on Customer notifications query | 30min | — |

**Estimated total effort:** ~2-3 days

---

## Phase 3 — Feature Completion (Sprint 3-4 — Weeks 5-8)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 3.1 | Implement Customer order history page (all statuses) | 1 day | E-04 |
| 3.2 | Implement Supplier forgot/reset password | 1 day | P-09 |
| 3.3 | Implement `is_read` notification marking + unread count badge | 1 day | P-10 |
| 3.4 | Fix booking to reference supplier's real tanker (not phantom TankerDetail) | 2 days | P-03 |
| 3.5 | Add no-available-supplier notification/timeout for pending orders | 2 days | E-08 |
| 3.6 | Admin document approval UI (dedicated page, not raw admin) | 2 days | E-06 |
| 3.7 | Email notification to supplier when documents are approved/rejected | 1 day | FR-16.3 |

**Estimated total effort:** ~10 days

---

## Phase 4 — Payment Integration (Sprint 5-6 — Weeks 9-12)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 4.1 | Integrate Razorpay (or PayU for India) payment gateway | 3 days | E-01 |
| 4.2 | Create payment initiation view (redirect to gateway) | 1 day | — |
| 4.3 | Create payment callback/webhook handler | 1 day | — |
| 4.4 | Create payment receipt generation | 1 day | — |
| 4.5 | Handle payment failure + retry flow | 1 day | — |
| 4.6 | Handle refund on order cancellation | 2 days | — |

**Estimated total effort:** ~10 days

---

## Phase 5 — Real-Time & Advanced Features (Sprint 7+ — Months 3+)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 5.1 | Add Django Channels + WebSocket support | 3 days | E-02 |
| 5.2 | Implement real-time order status notifications | 2 days | E-02 |
| 5.3 | Implement geo-distance order matching (replace pincode-only) | 3 days | E-03 |
| 5.4 | Implement supplier rating system | 2 days | E-05 |
| 5.5 | Add REST API layer (DRF) for mobile app support | 5 days | E-07 |
| 5.6 | Implement rate limiting on login/forgot-password | 1 day | Finding 13 |
| 5.7 | Upgrade Django from 4.2 to 5.x (before April 2026 LTS EOL) | 2 days | — |

**Estimated total effort:** ~18 days

---

## Phase 6 — Testing & DevOps (Ongoing)

| ID | Task | Effort | Ref |
|---|---|---|---|
| 6.1 | Write unit tests for all forms (validation rules) | 2 days | E-10 |
| 6.2 | Write unit tests for pricing logic | 1 day | — |
| 6.3 | Write integration tests for registration/booking/order flows | 3 days | — |
| 6.4 | Write signal/receiver tests (notification creation) | 1 day | — |
| 6.5 | Set up CI pipeline (GitHub Actions: lint + tests) | 1 day | — |
| 6.6 | Set up staging environment | 1 day | — |

---

## Roadmap Summary Timeline

```
Week 1:     Phase 0 — Security hardening (pre-production blockers)
Week 1-2:   Phase 1 — Bug fixes, code quality, dev environment
Week 3-4:   Phase 2 — Performance, database optimization
Week 5-8:   Phase 3 — Feature completion (order history, password reset, notifications)
Week 9-12:  Phase 4 — Payment integration
Month 3+:   Phase 5 — Real-time features, API, advanced matching
Ongoing:    Phase 6 — Test coverage, CI/CD
```

---

## Technical Debt Register

| Debt Item | Introduced By | Resolution |
|---|---|---|
| Duplicate `LocationDetail` model | Separate apps with same model | Phase 2.4 |
| Duplicate Celery tasks | Copy-paste across apps | Phase 1.5 |
| Phantom `TankerDetail` per booking | Design shortcut | Phase 3.4 |
| `Payment` model never used | Incomplete feature | Phase 4 |
| `is_read` never set | Incomplete feature | Phase 3.3 |
| `delivery_date` never populated | Unused field | Clean up in Phase 2 |
| Hardcoded rating "4.5" | Placeholder | Phase 5.4 |
| `haversine_distance` defined twice, never called | Copy-paste | Phase 2 cleanup |
| Test files empty | No test culture established | Phase 6 |
| `AUTH_USER_MODE` typo in settings | Typo | Clean up in Phase 1 |

---

## Decision Log (Open)

| Decision | Options | Recommendation |
|---|---|---|
| Payment gateway | Razorpay / PayU / Stripe | Razorpay (India-first, supports UPI) |
| Real-time layer | Django Channels / Server-Sent Events | Channels (full duplex, well-documented) |
| Mobile API | DRF REST / GraphQL | DRF REST (simpler, aligns with existing patterns) |
| Geo-matching | Geopy / PostGIS / Custom haversine | PostGIS with PostgreSQL (most powerful) |
| Email provider | Gmail SMTP / SendGrid / SES | SendGrid or SES for production scale |
| Hosting | Heroku / Railway / AWS / DigitalOcean | Unknown — Procfile and Dockerfile both present |
