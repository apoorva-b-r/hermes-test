# Fernhill Payments

This repository represents the Fernhill Payments platform, a demo estate built specifically to demonstrate Hermes, an API-discovery product that inspects source code, API documents, traffic logs, and a web front-end to classify routes as Active, Shadow, Zombie, Deprecated, or Unknown. Every route across this estate has been planted deliberately to evaluate discovery accuracy against a known answer key.

## Answer key

| Route | Host | What the code says | What the uploaded docs say | What the traffic logs say | Status it serves | Expected Hermes result |
|---|---|---|---|---|---|---|
| `GET /v2/invoices` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api`, referenced by web frontend | Documented in `billing-openapi.yaml` | Active traffic (~40% of requests, present in HAR) | 200 OK | **Active** |
| `GET /v2/invoices/{id}` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api`, called on item click in web frontend | Documented in `billing-openapi.yaml` | Active traffic (~25% of requests) | 200 OK | **Active** |
| `GET /v2/customers` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api`, called on page load in web frontend | Documented in `billing-openapi.yaml` | Active traffic (~20% of requests, present in HAR) | 200 OK | **Active** |
| `GET /api/v1/accounts` | `fernhill-demo-legacy.onrender.com` | Defined in `apps/legacy-api` | Documented in `legacy-postman.json` | Active traffic (~49% of legacy traffic) | 200 OK | **Active** |
| `GET /api/v1/accounts/{account_id}` | `fernhill-demo-legacy.onrender.com` | Defined in `apps/legacy-api` | Documented in `legacy-postman.json` | Active traffic (~37% of legacy traffic) | 200 OK | **Active** |
| `POST /admin/export` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api` | Undocumented (omitted from OpenAPI) | Zero traffic in logs | 202 Accepted | **Shadow (confirmed)** |
| `GET /internal/metrics` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api`, protected by `requireAuth` (`demo-metrics-token`) | Undocumented (omitted from OpenAPI) | Active traffic (~5% of requests, mostly 401s with occasional 200s) | 401 Unauthorized / 200 OK | **Shadow, requires login** |
| `GET /admin/users` | `fernhill-demo-admin.onrender.com` | Defined in `apps/admin-api`, protected by `@login_required` (`demo-admin-token`) | Undocumented | Zero traffic in logs | 401 Unauthorized / 200 OK | **Shadow, requires login** |
| `GET /api/v1/debug/config` | `fernhill-demo-legacy.onrender.com` | Defined in `apps/legacy-api`, deliberately exposed and unauthenticated | Undocumented (omitted from Postman) | Zero traffic in logs | 200 OK | **Shadow, unauthenticated** |
| `GET /health` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api` | Undocumented (omitted from OpenAPI) | Active traffic (~5% of requests) | 200 OK | **Shadow** |
| `GET /status` | `fernhill-demo-admin.onrender.com` | Defined in `apps/admin-api` | Undocumented | Zero traffic in logs | 200 OK | **Shadow** |
| `GET /v1/invoices` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api` (superseded by `/v2/invoices`) | Documented in `billing-openapi.yaml` (not marked deprecated) | Zero traffic across entire 120-day log | 200 OK | **Zombie (confirmed)** |
| `GET /v1/orders` | `fernhill-demo-billing.onrender.com` | Defined in `apps/billing-api` with `@deprecated` JSDoc and `Deprecation: true` response header | Documented in `billing-openapi.yaml` with `deprecated: true` (response 410) | Zero traffic across entire 120-day log | 410 Gone | **Deprecated** |
| `POST /api/v1/accounts/sync` | `fernhill-demo-legacy.onrender.com` | Defined in `apps/legacy-api` with `deprecated=True` | Documented in `legacy-postman.json` | Active traffic (~14% of legacy traffic) | 202 Accepted | **Deprecated** |
| `GET /legacy/report` | `fernhill-demo-billing.onrender.com` | Present on deployed `production` branch; deleted on `main` branch | Undocumented | Zero traffic across 120-day log | 200 OK | **Shadow and zombie candidate** |
| `POST /v2/reports/monthly` | `fernhill-demo-billing.onrender.com` | Not implemented anywhere in the codebase | Documented in `billing-openapi.yaml` | Zero traffic across entire 120-day log | 404 Not Found | **Unknown** (reason: documented in OpenAPI specification, but never implemented in source code and has no observed traffic) |

## How the demo works

- **Branch configuration**:
  - `production` is the deployed branch configured in [render.yaml](render.yaml) that powers the live demo services.
  - `main` has one extra commit that deletes `/legacy/report`. Consequently, Hermes (which reads the `main` branch in git) detects that the route was removed from source code, while runtime probes and production still serve it, flagging it as a shadow/zombie candidate.

- **Regenerating traffic logs on demo day**:
  To ensure log timestamps are fresh and align with the current date:
  ```bash
  python3 scripts/generate_logs.py
  ```
  The script uses `random.seed(7)` for deterministic generation and computes a rolling 120-day window ending at execution time (`now` in UTC). The first log entry will be within the window's first hour and the last log entry within the current hour, outputting:
  - `../fernhill-uploads/logs/api-access.log` (20,000 Nginx combined log entries)
  - `../fernhill-uploads/logs/legacy-access.jsonl` (3,000 JSON Lines entries)
  - `../fernhill-uploads/logs/web-session.har` (HAR 1.2 browser session recorded today)
