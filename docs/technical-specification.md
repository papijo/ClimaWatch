# ClimaWatch — Technical Specification

**Version:** 1.0 — Draft
**Date:** July 2026
**Authors:** Serge Ltd — Jonathan Ebhota & Ehi Ero-Omoighe
**Coverage:** 36 States + FCT
**Licence:** MIT

---

## Table of Contents

1. [Overview](#1-overview)
2. [Problem Statement](#2-problem-statement)
3. [Goals & Success Metrics](#3-goals--success-metrics)
4. [User Segments & Use Cases](#4-user-segments--use-cases)
5. [System Architecture](#5-system-architecture)
6. [Technical Stack](#6-technical-stack)
7. [Data Pipeline](#7-data-pipeline)
8. [AI Engine](#8-ai-engine)
9. [Risk Assessment Model](#9-risk-assessment-model)
10. [Alert System](#10-alert-system)
11. [API Design](#11-api-design)
12. [Frontend Surfaces](#12-frontend-surfaces)
13. [Authentication & Authorization](#13-authentication--authorization)
14. [Health Data Policy](#14-health-data-policy)
15. [NDPR Compliance](#15-ndpr-compliance)
16. [Security](#16-security)
17. [Performance & Reliability](#17-performance--reliability)
18. [Open Source](#18-open-source)
19. [Database Schema Reference](#19-database-schema-reference)
20. [Glossary](#20-glossary)

---

## 1. Overview

ClimaWatch is an open-source platform that correlates live climate data with public health risk indicators across Nigeria's 36 states and FCT. It ingests data from multiple open climate and health APIs, generates AI-powered risk assessments for each state, maps health facility vulnerability against those risks, and delivers early warnings to government contacts and the general public.

The platform is built by Serge Ltd and released as open source so that developers in other countries can fork and deploy it for their own regions with minimal configuration change.

> **Dual Mandate:** ClimaWatch serves two purposes simultaneously — **early warning** (surfacing alerts the moment climate conditions create disease-outbreak risk) and **continuous monitoring** (providing the analytical depth needed for policy decisions and health resource allocation).

---

## 2. Problem Statement

Nigeria faces compounding climate-health threats: flooding correlates with cholera and typhoid outbreaks; extreme heat strains capacity at under-resourced facilities; prolonged dry seasons elevate respiratory disease burden and food insecurity. These are documented, repeating patterns — yet no unified, publicly accessible platform currently:

- Correlates real-time climate data with health risk at state level
- Surfaces assessments in Nigeria's major languages — English, Hausa, Yoruba, Igbo
- Automatically alerts government contacts when risk thresholds are crossed
- Maps health facility vulnerability so planners can anticipate capacity strain
- Exposes an open dataset that researchers and civil society can access and build upon

ClimaWatch fills this gap.

---

## 3. Goals & Success Metrics

Success operates across three dimensions simultaneously — all are weighted equally.

### Open-source adoption

Developers can fork and deploy ClimaWatch for any country or region. Swapping `DATABASE_URL` plus state and data-source configuration is the only step needed to move between hosts or geographies.

### Real-world impact in Nigeria

Health and government agencies in Nigeria use the platform operationally — following state advisories, acting on alerts, and incorporating risk data into planning cycles.

### Technical credibility for Serge Ltd

The codebase, architecture, and documentation demonstrate Serge Ltd's capability to build production-grade, socially relevant software at a public standard.

---

## 4. User Segments & Use Cases

### User Segments

| Segment | Description |
|---|---|
| **General Public** | Citizens, journalists, researchers, civil society. Check risk levels, read AI advisories in their language, subscribe to state alerts, and access open data. |
| **Government Contacts** | State health officials and ministry contacts. Receive email alerts when a state reaches HIGH or CRITICAL risk. Alerts are informational — no response workflow required. |
| **Serge Admin** | Internal Serge Ltd staff only. Manage contacts, monitor assessments and logs, trigger manual runs, and oversee the data pipeline. No public registration path. |

### General Public — Use Cases

- **Personal health decisions** — checking current risk in their state before travel or outdoor activity
- **Language-native advisories** — reading AI guidance in English, Hausa, Yoruba, or Igbo
- **Transparency access** — journalists and researchers using the public API to build stories or analyses
- **Alert subscription** — opting in to receive email alerts for one or more states

### Government Contacts — Use Cases

- Receive email when a state transitions to HIGH or CRITICAL
- Alerts are informational only — no acknowledgement, escalation, or response tracking is implemented

### Serge Admin — Use Cases

- Monitor KPIs: critical-state count, active alerts, last assessment time
- Inspect per-state risk assessments and score breakdowns
- Manage government contact list (add, edit, delete)
- Trigger manual AI assessments for specific states
- View pipeline status and trigger manual ingestion runs for live API sources
- Review risk state-change history (audit log)

---

## 5. System Architecture

ClimaWatch is a **modular monolith**. One codebase, one deployment unit per service. This is a deliberate, maintained constraint — microservices will not be introduced without an explicit architectural decision.

### Repository Structure

```
climawatch/
  backend/           # Python 3.12 + FastAPI
  frontend-public/   # Next.js 14 App Router
  frontend-admin/    # React 18 + Vite + TypeScript
  docker-compose.yml # Full local stack
  .env.example       # Keys with empty values only — never commit .env
```

### Backend Module Structure

```
backend/app/modules/
  data_pipeline/         # Open-Meteo, NASA POWER, NOAA CDO ingestion
  scheduler/             # APScheduler — adaptive 2–12 hr cycle
  ai_engine/             # GPT-4o prompts + structured JSON parsing
  vulnerability_scoring/ # LGA-level and facility risk scoring
  risk_manager/          # State risk transitions and history logging
  alert_engine/          # Active alert management + Resend email dispatch
  api/                   # FastAPI route handlers (public / user / admin)
  auth/                  # JWT + bcrypt
```

### Deployment Topology

| Service | Platform | Notes |
|---|---|---|
| FastAPI backend | Render Web Service | Always-on, auto-deploy from main |
| Next.js public site | Vercel | Edge CDN, auto-deploy from main |
| React admin panel | Render Static Site | Auto-deploy from main |
| PostgreSQL | Supabase | Standard connection string only — portable to any PostgreSQL host by changing `DATABASE_URL` |

> **Database Portability:** The only Supabase touchpoint is the `DATABASE_URL` environment variable. Supabase SDK, Auth, Realtime, Storage, and RLS policies are never used. Changing `DATABASE_URL` is the only step needed to migrate to any other PostgreSQL host.

---

## 6. Technical Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Async, Pydantic v2 validation |
| Public website | Next.js 14 (App Router) | SSR + static, Vercel edge |
| Admin panel | React 18 + Vite + TypeScript | |
| Admin UI library | shadcn/ui | new-york style, slate base, CSS variables |
| Database | PostgreSQL via Supabase | Accessed via standard connection string only |
| ORM / Migrations | SQLAlchemy + Alembic | |
| AI engine | OpenAI API — `gpt-4o` | Fixed. Do not change without explicit instruction. |
| Maps | Mapbox GL JS | Dark-v11 style, risk-coded state markers |
| Email | Resend | Sender: hello@weareserge.com |
| Scheduler | APScheduler | In-process background task inside FastAPI |
| Auth | JWT (python-jose) + bcrypt | No external auth provider |
| i18n | next-intl | EN, HA, YO, IG — never hardcoded in JSX |
| HTTP client | httpx (async) | |

---

## 7. Data Pipeline

### Data Sources

| Source | Type | Cadence | Auth | Admin-triggerable |
|---|---|---|---|---|
| Open-Meteo | Live API | Hourly | None | Yes |
| NASA POWER | Live API | Daily | None | Yes |
| NOAA CDO | Live API | Weekly | `NOAA_TOKEN` | Yes |
| NHFR via HDX | Dataset ingestion | Monthly | Free download | No — manual upload |
| NCDC Data Portal | Dataset ingestion | Weekly | Free download | No — manual upload |
| WHO AFRO Bulletin | Parsed report | Weekly | Free | No — manual upload |

Live API sources can be triggered from the admin pipeline page. Dataset sources require manual file upload — they expose no programmable trigger endpoint.

### Adaptive Scheduler

- **Default cycle** — 12 hours for all 37 locations
- **Elevated cycle** — if a state is MODERATE or above, the scheduler switches to 2–3 hours for that state automatically
- **Return to default** — if a state returns to LOW for two consecutive cycles, it reverts to 12-hour cadence
- Runs in-process inside FastAPI as an APScheduler background task — does not block API responses
- Background tasks create their own `SessionLocal` database session, independent from request-scoped sessions

---

## 8. AI Engine

The AI engine generates a structured risk assessment for each Nigerian state by sending a carefully constructed prompt to OpenAI's GPT-4o and parsing the JSON response.

### Input Context (per state prompt)

- The last 3 risk assessments for the state — for trend awareness
- Current live climate readings (temperature, humidity, rainfall, wind speed)
- Active disease alerts from NCDC and WHO AFRO
- Health facility data and vulnerability scores for the state

### Output Contract

The API is always called with `response_format={"type": "json_object"}` to guarantee valid JSON. The response is validated against the `RiskAssessment` Pydantic v2 schema before being written to the database. Invalid responses are rejected — not stored.

### Multi-language Advisories

Each assessment includes health advisories in four languages, stored as `advisory_en`, `advisory_ha`, `advisory_yo`, and `advisory_ig`. Language selection is the user's choice on the public site. The admin panel shows all four via a tab interface.

> **Model Constraint:** The model is fixed at `gpt-4o`. Do not change this without an explicit instruction and a corresponding update to this specification. Model changes affect assessment quality and output format — they are significant decisions, not configuration tweaks.

---

## 9. Risk Assessment Model

### Risk Tiers

| Level | Meaning | Alert triggered | Scheduler cadence |
|---|---|---|---|
| `LOW` | Normal conditions | No | 12 hours |
| `MODERATE` | Elevated attention advised | No | 2–3 hours |
| `HIGH` | Immediate action advisable | Yes — email alert | 2–3 hours |
| `CRITICAL` | Emergency response warranted | Yes — email alert | 2–3 hours |

### Scoring Dimensions

Each assessment produces four numeric scores on a 0–100 scale:

- **Climate score** — temperature anomalies, rainfall, humidity, extreme-weather indicators
- **Health score** — active disease alerts, historical outbreak patterns, seasonal disease burden
- **Vulnerability score** — facility density, capacity, LGA-level socio-economic risk factors
- **Overall score** — weighted composite of the three scores above

### State Transitions

Every change in a state's risk level is recorded in `risk_state_changes` with a timestamp, previous level, new level, and an AI-generated reason string. This forms an audit trail visible in the admin logs page.

---

## 10. Alert System

Alerts are generated when a state transitions to HIGH or CRITICAL, serving two channels simultaneously:

- **Website** — active alerts appear on the public site via `GET /api/alerts/active` in real time
- **Email** — government contacts registered for the affected state receive an email via Resend, including a one-click unsubscribe link

Alerts are informational only. There is no acknowledgement, escalation path, or response tracking. Alert history is paginated and available in the admin panel and via the public `/api/alerts/history` endpoint.

---

## 11. API Design

All endpoints return JSON. Public endpoints use cursor-based pagination. Admin endpoints use page/limit (offset-based) pagination with the response shape `{items, total, page, limit, total_pages}`, default limit 10, maximum 100.

### Public — No Auth Required

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/states` | All 37 states with current risk level and metadata |
| GET | `/api/states/{state_id}` | Full state detail including latest assessment |
| GET | `/api/states/{state_id}/lgas` | LGA-level risk breakdown |
| GET | `/api/facilities` | Health facilities with risk and vulnerability scores |
| GET | `/api/alerts/active` | All currently active HIGH and CRITICAL alerts |
| GET | `/api/alerts/history` | Paginated alert history (cursor-based) |
| GET | `/api/disease-alerts` | Active disease alerts from NCDC and WHO AFRO |
| GET | `/api/forecasts/{state_id}` | Disease and surge forecasts for a state |

### Authenticated — JWT Required

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new public user account |
| POST | `/api/auth/login` | Login and receive a JWT |
| GET | `/api/me/subscriptions` | List the user's active alert subscriptions |
| POST | `/api/me/subscriptions` | Subscribe to alerts for a state |
| DELETE | `/api/me` | Delete account and all personal data (NDPR right to erasure) |

### Admin — JWT + Admin Role Required

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/assessments` | Paginated assessments — search, sort, state filter |
| GET | `/api/admin/logs` | Paginated risk state-change log — search, sort |
| GET | `/api/admin/contacts` | Paginated government contacts — search, sort |
| POST | `/api/admin/contacts` | Create a government contact |
| PUT | `/api/admin/contacts/{id}` | Update an existing contact |
| DELETE | `/api/admin/contacts/{id}` | Delete a contact |
| POST | `/api/admin/trigger/{state_id}` | Manually trigger an AI assessment for a state |
| GET | `/api/admin/pipeline/status` | Pipeline status for all 6 data sources |
| POST | `/api/admin/pipeline/trigger/{source}` | Trigger a manual ingestion run for a live API source |

---

## 12. Frontend Surfaces

### Public Website — Next.js 14

- App Router architecture — SSR with Vercel edge CDN delivery
- i18n via next-intl — EN, HA, YO, IG. All strings in `messages/` JSON files. Zero hardcoded JSX strings. Adding a language requires only a new messages file.
- Mapbox GL JS interactive map — state markers color-coded by risk level, hover popup, click for full detail
- Mobile-first — optimised for Nigerian users on mobile connections. Target: under 100 KB initial JS; aggressive code splitting via Next.js.

### Admin Panel — React 18 + Vite

- Component library: shadcn/ui (new-york style, slate base, CSS variable theming)
- Collapsible sidebar — 220 px expanded, 60 px icon-only when collapsed; state persisted to `localStorage`
- Pages: Dashboard (KPIs + Mapbox map + state table), Contacts, Assessments, Logs, Pipeline
- All tables have search, column sort, and page/limit pagination via shared `TableToolbar` and `TablePagination` components
- Dark/light mode via Tailwind `darkMode: 'class'`
- Serge staff only — no public registration, no self-service admin creation

---

## 13. Authentication & Authorization

- JWT-based, implemented with `python-jose` — issued on login, validated on every protected route
- Passwords hashed with bcrypt — plaintext passwords are never stored, logged, or retained after initial receipt
- JWT secret lives in `JWT_SECRET` — never hardcoded
- Admin accounts seeded directly in the database — no self-registration path for the admin role exists
- Admin role encoded in the JWT payload, checked on every admin route handler
- Public users self-register via `POST /api/auth/register` — they receive the standard user role
- No authentication middleware is applied to public API routes
- Supabase Auth is not used — `DATABASE_URL` is the sole Supabase touchpoint

---

## 14. Health Data Policy

ClimaWatch surfaces aggregate, population-level health intelligence. It does not handle individual health data of any kind. This boundary is a design constraint, not a future limitation to be relaxed.

### What ClimaWatch Handles

- Disease alerts from NCDC and WHO AFRO — aggregated, non-identifiable, institutional sources
- Health facility locations, types, and capacity indicators — institutional data, not patient data
- LGA-level and state-level risk scores derived from aggregated indicators
- Climate readings and AI-derived assessments
- User email addresses and state subscription preferences (for alert delivery only)

### What ClimaWatch Does NOT Handle

- Individual patient records of any kind
- Clinical data — diagnoses, treatments, medications, lab results
- Personally identifiable health information (PIHI)
- Any data that could identify an individual's health status
- Any data subject to clinical confidentiality obligations

> **Advisory Disclaimer:** AI-generated advisories are public health guidance at the population level — they are not medical advice. ClimaWatch does not diagnose, treat, or make clinical recommendations for individuals. This disclaimer must appear on the public website, in the app, and in all alert emails.

---

## 15. NDPR Compliance

ClimaWatch collects personal data from Nigerian residents, triggering obligations under the Nigeria Data Protection Regulation (NDPR) 2019.

### Personal Data Collected

| Data | Purpose | Retention |
|---|---|---|
| Email address | Account authentication; alert delivery | Until account deletion |
| Password hash | Authentication only | Until account deletion |
| State subscription list | Filtering alert delivery | Until subscription cancelled or account deleted |

### Implementation Requirements

- **Privacy Policy** — published at `/privacy`, accessible before registration, written in plain language
- **Consent** — explicit opt-in checkbox for email subscriptions (not pre-ticked); consent logged with timestamp
- **Data minimization** — only the fields above are collected; no unnecessary profile data
- **Right to access** — users can retrieve their own data via the authenticated API
- **Right to erasure** — `DELETE /api/me` removes all personal data associated with the account
- **Unsubscribe** — every alert email must include a one-click unsubscribe link
- **Data Processing Agreement** — Resend (email processor) must have a signed DPA with Serge Ltd before production launch
- **Breach notification** — any confirmed data breach reported to NITDA within 72 hours
- **Data Protection Officer** — Serge Ltd designates a DPO or compliance contact, published on the privacy policy page

---

## 16. Security

- **Secrets** — all secrets in environment variables. Required: `DATABASE_URL`, `OPENAI_API_KEY`, `RESEND_API_KEY`, `JWT_SECRET`, `MAPBOX_TOKEN`, `NOAA_TOKEN`. `.env` is never committed — `.env.example` holds empty-value placeholders only.
- **SQL injection** — prevented by SQLAlchemy ORM; raw SQL is not used in application code
- **XSS** — prevented by React's default output escaping on both frontends
- **HTTPS** — enforced on all surfaces (Vercel and Render enforce HTTPS in production)
- **CORS** — configured to allow only known frontend origins
- **Input validation** — Pydantic v2 validates all API inputs at system boundaries
- **Rate limiting** — required on `/api/auth/register` and `/api/auth/login` before production launch
- **Admin isolation** — admin accounts cannot be created via any user-facing flow; seeded only

---

## 17. Performance & Reliability

Reliability and performance are first-class, equally weighted requirements.

### Reliability

- Target availability: 99.5% uptime
- Scheduler runs in-process and does not block API responses
- Background tasks use `asyncio.ensure_future` — failures do not affect the request cycle
- Background tasks create and close their own database sessions independently of request-scoped sessions

### Performance

- Public site target: under 100 KB initial JS bundle; aggressive Next.js code splitting
- Mobile-first throughout — optimised for Nigerian users on mobile connections
- Vercel edge CDN serves the public site from the closest region to the user
- API response time target: under 500 ms for public endpoints under normal load
- Next.js Image component used for all media — automatic resizing and WebP conversion

---

## 18. Open Source

ClimaWatch is released under the **MIT licence** — chosen for maximum adoption with minimal friction.

### Self-hosting

Any developer or organisation can run a full local instance with a single command:

```bash
docker-compose up   # starts backend + postgres
```

The only required step is populating `.env` from `.env.example`.

### Geographic Replicability

Deploying for a new country or region requires:

1. Replacing the `states` seed data with the target geography's regions
2. Updating data-source configuration to point at regional climate and disease APIs
3. Updating i18n message files with the relevant languages
4. Setting a new `DATABASE_URL`

No changes to business logic, the AI engine, the alert system, or the API structure are required.

### Contribution Constraints

- Do not introduce microservices — this is and will remain a modular monolith
- Do not import the Supabase SDK — `DATABASE_URL` is the only Supabase touchpoint
- Do not hardcode UI strings in JSX — use next-intl message files
- Do not change the AI model without updating this specification
- All secrets must live in environment variables

---

## 19. Database Schema Reference

All tables use UUID primary keys. All timestamps are stored in UTC.

| Table | Description |
|---|---|
| `states` | 37 Nigerian states + FCT with coordinates, region, capital |
| `climate_readings` | Raw climate readings per state per source and timestamp |
| `risk_assessments` | AI-generated assessment per state — scores, risk level, advisories in 4 languages |
| `risk_state_changes` | Audit log of every risk level transition per state |
| `active_alerts` | Currently active HIGH/CRITICAL alerts surfaced on the public site |
| `government_contacts` | Contacts per state for email alert dispatch |
| `users` | Registered public users — email + bcrypt password hash + role |
| `user_subscriptions` | User-to-state alert subscription mappings |
| `health_facilities` | NHFR facility locations, types, and capacity indicators |
| `facility_risk_scores` | Per-facility vulnerability scores derived from climate and capacity data |
| `lga_vulnerability_scores` | Aggregated vulnerability scores at LGA level |
| `disease_alerts` | Active NCDC and WHO AFRO disease alerts |

---

## 20. Glossary

| Term | Definition |
|---|---|
| FCT | Federal Capital Territory (Abuja) — treated as a state equivalent throughout the platform |
| LGA | Local Government Area — the administrative subdivision below state level in Nigeria |
| NCDC | Nigeria Centre for Disease Control — primary source for national disease alerts |
| NHFR | National Health Facility Registry — source for facility location and capacity data |
| NDPR | Nigeria Data Protection Regulation 2019 — Nigeria's primary data privacy framework |
| NITDA | National Information Technology Development Agency — the NDPR regulatory authority |
| WHO AFRO | World Health Organization Africa Region — source for regional disease bulletins |
| GPT-4o | The specific OpenAI model used by the AI engine — fixed, not configurable without a spec change |
| PIHI | Personally Identifiable Health Information — any data that identifies an individual's health status. ClimaWatch never handles PIHI. |
| Modular monolith | Architecture where a codebase is organised into modules but deployed as a single unit — the opposite of microservices |
| APScheduler | Advanced Python Scheduler — the in-process task scheduler running the climate assessment cycle |
| DPA | Data Processing Agreement — a contractual requirement between Serge Ltd and any third-party data processor (e.g. Resend) |
