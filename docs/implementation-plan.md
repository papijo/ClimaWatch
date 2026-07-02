# ClimaWatch — Project Implementation Plan

> **Project:** AI-powered climate-health intelligence platform for Nigeria
> **Owner:** Serge Ltd — Jonathan Ebhota & Ehi Ero-Omoighe
> **Programme:** UNICEF Climate Ventures Programme (Areas 1, 2 & 3)
> **Stack:** Python 3.12 + FastAPI · Next.js 14 · React 18 + Vite · PostgreSQL · OpenAI API (gpt-4o)

---

## Project Completion Summary

| Phase | Name | Tasks | Done | % Complete |
|:-----:|------|:-----:|:----:|:----------:|
| 0 | Foundation & Infrastructure | 19 | 19 | 100% |
| 1 | Database Migrations & Seed Data | 8 | 8 | 100% |
| 2 | Data Ingestion Pipeline | 11 | 11 | 100% |
| 3 | AI Engine (OpenAI Integration) | 8 | 8 | 100% |
| 4 | Vulnerability Scoring | 7 | 7 | 100% |
| 5 | Risk Manager | 6 | 6 | 100% |
| 6 | Adaptive Scheduler | 7 | 7 | 100% |
| 7 | Alert Engine | 7 | 7 | 100% |
| 8 | REST API — Public Routes | 10 | 10 | 100% |
| 9 | REST API — Auth & User Routes | 8 | 8 | 100% |
| 10 | REST API — Admin Routes | 7 | 7 | 100% |
| 11 | Public Frontend — Setup & Config | 8 | 8 | 100% |
| 12 | Public Frontend — Core Pages | 12 | 12 | 100% |
| 13 | Public Frontend — i18n & Language Switcher | 5 | 5 | 100% |
| 14 | Admin Panel — Setup | 6 | 6 | 100% |
| 15 | Admin Panel — Features | 10 | 10 | 100% |
| 16 | Testing & QA | 9 | 0 | 0% |
| 17 | Deployment & Go-Live | 9 | 0 | 0% |
| | **TOTAL** | **157** | **139** | **88.5%** |

---

## Build Order Rationale

The build follows a strict dependency chain:
**Foundation → Data → AI → Scoring → Risk → Scheduler → Alerts → API → Frontend → Admin → Test → Deploy**

Each phase depends on the one before it being fully functional. Do not skip ahead — the AI engine requires real climate data, the scheduler requires the AI engine, and the frontend requires a working API.

---

## Phase 0 — Foundation & Infrastructure
> **Goal:** A runnable FastAPI app with all models defined, Alembic configured, and the full module structure in place.
> **Status:** ✅ Complete

| # | Task | Status |
|---|------|:------:|
| 1 | Create `backend/` directory structure with all 8 module folders | [x] |
| 2 | Write `requirements.txt` with all pinned dependencies | [x] |
| 3 | Write `.env.example` with all 6 required env var keys | [x] |
| 4 | Create `app/config.py` — Pydantic Settings loading from `.env` | [x] |
| 5 | Create `app/database.py` — SQLAlchemy engine, `SessionLocal`, `Base`, `get_db` | [x] |
| 6 | Create SQLAlchemy model: `State` (36 states + FCT) | [x] |
| 7 | Create SQLAlchemy model: `ClimateReading` | [x] |
| 8 | Create SQLAlchemy model: `RiskAssessment` (with 4-language advisory fields) | [x] |
| 9 | Create SQLAlchemy model: `RiskStateChange` | [x] |
| 10 | Create SQLAlchemy model: `ActiveAlert` | [x] |
| 11 | Create SQLAlchemy model: `GovernmentContact` | [x] |
| 12 | Create SQLAlchemy model: `User` (JWT auth, no Supabase) | [x] |
| 13 | Create SQLAlchemy model: `UserSubscription` | [x] |
| 14 | Create SQLAlchemy model: `HealthFacility` (v2) | [x] |
| 15 | Create SQLAlchemy model: `FacilityRiskScore` (v2) | [x] |
| 16 | Create SQLAlchemy model: `LGAVulnerabilityScore` (v2) | [x] |
| 17 | Create SQLAlchemy model: `DiseaseAlert` (v2, nullable state for national alerts) | [x] |
| 18 | Configure Alembic — `alembic.ini`, `env.py` (reads `DATABASE_URL` from env, imports all models) | [x] |
| 19 | Create `app/main.py` — FastAPI app, CORS middleware, lifespan, all routers mounted | [x] |

---

## Phase 1 — Database Migrations & Seed Data
> **Goal:** All 12 tables exist in the PostgreSQL database and are pre-populated with Nigeria's 37 states/FCT. An admin account is seeded directly — no registration flow.
> **Prerequisite:** Phase 0 complete, `DATABASE_URL` in `.env` pointing to a live PostgreSQL instance.

| # | Task | Status |
|---|------|:------:|
| 1 | Generate initial Alembic migration (`alembic revision --autogenerate -m "initial schema"`) | [x] |
| 2 | Review and clean generated migration file — verify all 12 tables, enums, FKs, and indexes | [x] |
| 3 | Run `alembic upgrade head` and confirm all tables created with correct schema | [x] |
| 4 | Write `backend/scripts/seed_states.py` — idempotent seed for all 37 states/FCT with name, code, region, capital, latitude, longitude | [x] |
| 5 | Write `backend/scripts/seed_admin.py` — create Serge admin account with bcrypt-hashed password, seeded directly to DB | [x] |
| 6 | Write `backend/scripts/seed_government_contacts.py` — placeholder contacts per state (ministry of health) | [x] |
| 7 | Add a `Makefile` or `scripts/run_seeds.sh` to run all seeds in order | [x] |
| 8 | Verify: connect to DB with a SQL client, confirm row counts and FK integrity | [x] |

---

## Phase 2 — Data Ingestion Pipeline
> **Goal:** For any given state, the pipeline can fetch current climate data from all three live APIs and store a `ClimateReading` record. Offline datasets (NHFR, NCDC, WHO AFRO) can be ingested from local files.
> **Prerequisite:** Phase 1 complete (states table populated).

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `open_meteo.py` — async `fetch()` + `parse()`, handle HTTP errors, store `ClimateReading` | [x] |
| 2 | Implement `nasa_power.py` — async `fetch()` + `parse()`, handle -999 fill values from NASA | [x] |
| 3 | Build `backend/data/state_noaa_stations.json` — mapping of each state ID to nearest NOAA GHCND station ID | [x] |
| 4 | Implement `noaa_cdo.py` — async `fetch()` using station mapping + `parse()`, handle rate limits (1 req/s) | [x] |
| 5 | Implement pipeline orchestrator `data_pipeline/runner.py` — calls all three sources per state, merges readings, writes `ClimateReading` to DB | [x] |
| 6 | Implement `nhfr.py` bulk ingest command — reads a downloaded HDX CSV, upserts `HealthFacility` records (state resolved by name), idempotent | [x] |
| 7 | Implement `ncdc.py` — parses a downloaded NCDC sitrep JSON into `DiseaseAlert` records | [x] |
| 8 | Implement `who_afro.py` — parses WHO AFRO bulletin JSON into `DiseaseAlert` records | [x] |
| 9 | Add retry logic with exponential backoff to all three live API clients (httpx) | [x] |
| 10 | Write `backend/scripts/ingest_nhfr.py` — CLI script to run NHFR ingest from a given CSV path | [x] |
| 11 | Manually run pipeline for 5 test states and confirm `climate_readings` rows in DB | [x] |

---

## Phase 3 — AI Engine (Claude Integration)
> **Goal:** Given a state ID, the AI engine fetches context, calls Claude, validates the JSON response, and writes a `RiskAssessment` to the database.
> **Prerequisite:** Phase 2 complete (climate readings exist). `OPENAI_API_KEY` in `.env`.

| # | Task | Status |
|---|------|:------:|
| 1 | Implement context builder in `ai_engine/context.py` — fetches latest climate reading, last 3 assessments, active disease alerts, and facility summary for a given state | [x] |
| 2 | Refine system prompt in `ai_engine/prompts.py` — include explicit scoring rubric and example JSON output to reduce hallucination | [x] |
| 3 | Implement async OpenAI call in `ai_engine/client.py` — use `AsyncOpenAI`, handle timeout 60s | [x] |
| 4 | Implement JSON extraction helper — strips markdown code fences if model wraps JSON in ` ```json ``` ` | [x] |
| 5 | Validate raw response against `RiskAssessmentResponse` Pydantic schema — raise `ValueError` on invalid structure | [x] |
| 6 | Implement `ai_engine/service.py` — orchestrates context build → OpenAI call → validation → DB write, updates `state.current_risk_level` | [x] |
| 7 | Test AI engine end-to-end against 3 states: Lagos (LOW, 20), Sokoto (MODERATE, 41), Plateau (MODERATE, 45) | [x] |
| 8 | Document the prompt design and scoring methodology in `docs/ai-scoring-methodology.md` | [x] |

---

## Phase 4 — Vulnerability Scoring
> **Goal:** Every LGA has a `LGAVulnerabilityScore` and every health facility has a `FacilityRiskScore`. These scores feed into the AI engine context.
> **Prerequisite:** Phase 2 complete (NHFR facilities ingested), Phase 1 complete (states + LGAs known).

| # | Task | Status |
|---|------|:------:|
| 1 | Define scoring input data sources — document which fields drive each sub-score (population density from NBS, facility count from NHFR, climate exposure from climate readings) | [x] |
| 2 | Implement `lga_scorer.py` fully — weighted formula: population density (35%), health access (40%), climate exposure (25%) | [x] |
| 3 | Implement `facility_scorer.py` fully — weighted formula: flood risk (30%), heat stress (25%), disease burden (25%), infrastructure vulnerability (20%) | [x] |
| 4 | Build `vulnerability_scoring/runner.py` — batch scoring runner that scores all LGAs per state and all facilities per LGA | [x] |
| 5 | Write `backend/scripts/run_scoring.py` — CLI to trigger batch scoring for all states | [x] |
| 6 | Run batch scoring, confirm `lga_vulnerability_scores` and `facility_risk_scores` populated | [x] |
| 7 | Write unit tests for scoring formulas — verify weighted averages, boundary values (0 and 100) | [x] |

---

## Phase 5 — Risk Manager
> **Goal:** Risk level transitions are tracked, logged, and drive downstream effects (scheduler, alerts). Two consecutive LOW cycles return a state to the 12-hour schedule.
> **Prerequisite:** Phase 3 complete (assessments being written).

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `risk_manager/manager.py` `apply_risk_transition()` fully — writes `RiskStateChange`, updates `State.current_risk_level`, commits in a single transaction | [x] |
| 2 | Implement `get_consecutive_low_count()` — queries last N `RiskAssessment` records for a state, returns count of consecutive LOW | [x] |
| 3 | Implement `should_downgrade_schedule()` — returns `True` if last 2 assessments are both LOW | [x] |
| 4 | Wire `apply_risk_transition()` into `ai_engine/service.py` so every assessment run triggers a transition check | [x] |
| 5 | Add `risk_manager` callback hook so alert engine is notified on HIGH/CRITICAL transitions | [x] |
| 6 | Write unit tests: LOW→MODERATE, MODERATE→HIGH, HIGH→LOW, LOW×2 downgrade detection | [x] |

---

## Phase 6 — Adaptive Scheduler
> **Goal:** All 37 states are assessed on a 12-hour cycle by default. States at MODERATE or above switch to a 2-3-hour cycle automatically and return to 12-hour after two consecutive LOW assessments.
> **Prerequisite:** Phase 5 complete (risk transitions working), Phase 3 complete (AI engine service exists).

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `scheduler/scheduler.py` `start()` — registers a job per state at startup using the state's current risk level to determine initial cycle | [x] |
| 2 | Implement full assessment job function `run_state_assessment(state_id)` — chains: data pipeline → AI engine → risk manager → alert engine → reschedule | [x] |
| 3 | Implement `reschedule_state()` — reschedules APScheduler job: MODERATE/HIGH/CRITICAL → 2hr, LOW (after 2 consecutive) → 12hr | [x] |
| 4 | Wire lifespan in `app/main.py` — on startup, load all active states from DB, register jobs; on shutdown, graceful APScheduler stop | [x] |
| 5 | Implement `POST /api/admin/trigger/{state_id}` — immediately enqueues a one-off assessment job for the given state | [x] |
| 6 | Add `GET /api/admin/scheduler/status` — returns all registered jobs with state, next run time, and current interval | [x] |
| 7 | Manual test: trigger an assessment for Lagos via admin endpoint, confirm job completed, DB updated | [x] |

---

## Phase 7 — Alert Engine
> **Goal:** HIGH and CRITICAL risk transitions create `ActiveAlert` records visible on the website. Subscribed users receive a Resend email in their preferred language within minutes of a risk change.
> **Prerequisite:** Phase 5 complete (transitions firing), Phase 1 complete (subscribers exist). `RESEND_API_KEY` in `.env`.

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `website_alerts.py` — `create_alert()` triggered on HIGH/CRITICAL transition; `resolve_alerts()` triggered on LOW/MODERATE transition | [x] |
| 2 | Build subscriber lookup `alert_engine/subscribers.py` — queries `user_subscriptions` filtered by state and risk level threshold | [x] |
| 3 | Build branded HTML email template — includes state name, risk level, advisory in user's preferred language, unsubscribe link | [x] |
| 4 | Implement `email_dispatch.py` batch sender — loops subscribers, calls Resend, logs successes/failures | [x] |
| 5 | Wire alert engine into risk manager callback from Phase 5 — HIGH/CRITICAL → create alert + dispatch emails | [x] |
| 6 | Wire disease alert ingestion — when NCDC/WHO AFRO parser produces a new `DiseaseAlert`, create a corresponding `ActiveAlert` if state is affected | [x] |
| 7 | Test: manually trigger a HIGH assessment for a state with a test subscriber, confirm email received and `active_alerts` row created | [x] |

---

## Phase 8 — REST API — Public Routes
> **Goal:** All public endpoints documented in CLAUDE.md are live, return correct data shapes, and use cursor-based pagination where applicable. No authentication required.
> **Prerequisite:** Phases 1-7 complete (data exists in all tables).

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `GET /api/states` — all 37 states with `current_risk_level`, ordered by name | [x] |
| 2 | Implement `GET /api/states/{state_id}` — full state detail including latest assessment | [x] |
| 3 | Implement `GET /api/states/{state_id}/lgas` — LGA vulnerability scores sorted by score descending | [x] |
| 4 | Implement `GET /api/facilities` — health facilities with latest risk score, optional `?state_id=` filter | [x] |
| 5 | Implement `GET /api/alerts/active` — all active HIGH/CRITICAL alerts ordered by `started_at` descending | [x] |
| 6 | Implement `GET /api/alerts/history` — resolved alerts with cursor-based pagination (`?cursor=&limit=`) | [x] |
| 7 | Implement `GET /api/disease-alerts` — active NCDC/WHO alerts ordered by `reported_at` descending | [x] |
| 8 | Implement `GET /api/forecasts/{state_id}` — latest `RiskAssessment` with all advisory language fields | [x] |
| 9 | Define Pydantic output schemas for all responses — never expose `password_hash`, internal IDs remain UUIDs | [x] |
| 10 | Write API integration tests for all 8 public endpoints using `TestClient` | [x] |

---

## Phase 9 — REST API — Auth & User Routes
> **Goal:** Public users can register, log in (JWT), and manage state subscriptions. Passwords are bcrypt-hashed. No Supabase Auth.
> **Prerequisite:** Phase 8 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `POST /api/auth/register` — validate email uniqueness, hash password, return `{id, email}` | [x] |
| 2 | Implement `POST /api/auth/login` — verify bcrypt hash, return `{access_token, token_type}` | [x] |
| 3 | Implement `get_current_user` dependency — decodes JWT, fetches active user from DB, raises 401 on failure | [x] |
| 4 | Implement `GET /api/me/subscriptions` — returns user's active subscriptions with state detail | [x] |
| 5 | Implement `POST /api/me/subscriptions` — upsert subscription for a state with notification preferences | [x] |
| 6 | Add `DELETE /api/me/subscriptions/{state_id}` — soft-delete (set `is_active = false`) | [x] |
| 7 | Input validation: password minimum 8 chars, email format validation via Pydantic `EmailStr` | [x] |
| 8 | Write integration tests: register, login, get token, access protected route, invalid token returns 401 | [x] |

---

## Phase 10 — REST API — Admin Routes
> **Goal:** Admin users (seeded, not self-registered) can manage contacts, view logs, view assessments, and manually trigger state assessments. All routes require JWT + admin role.
> **Prerequisite:** Phase 9 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Implement `require_admin` dependency — wraps `get_current_user`, checks `role == "admin"`, raises 403 | [x] |
| 2 | Implement `GET /api/admin/logs` — paginated `RiskStateChange` history across all states | [x] |
| 3 | Implement `GET /api/admin/assessments` — paginated assessments, optional `?state_id=` filter | [x] |
| 4 | Implement `POST /api/admin/contacts` — create government contact for a state | [x] |
| 5 | Implement `PUT /api/admin/contacts/{id}` — update contact fields | [x] |
| 6 | Implement `DELETE /api/admin/contacts/{id}` — hard delete | [x] |
| 7 | Write integration tests: admin-only routes return 403 for regular users, 401 for unauthenticated | [x] |

---

## Phase 11 — Public Frontend — Setup & Config
> **Goal:** A working Next.js 14 App Router project with next-intl, Mapbox, and Tailwind configured. The app can talk to the backend API and renders in all four languages.
> **Prerequisite:** Phase 10 complete (full backend API live at a known URL). `MAPBOX_TOKEN` available.

| # | Task | Status |
|---|------|:------:|
| 1 | Initialise Next.js 14 App Router project in `frontend-public/` with TypeScript | [x] |
| 2 | Install and configure `next-intl` — set up `i18n.ts`, `middleware.ts`, locale routing (`/en`, `/ha`, `/yo`, `/ig`) | [x] |
| 3 | Create base message files: `messages/en.json`, `messages/ha.json`, `messages/yo.json`, `messages/ig.json` — all UI strings, no hardcoded text in JSX | [x] |
| 4 | Install and configure Tailwind CSS + base design system (risk level colour tokens: LOW=green, MODERATE=yellow, HIGH=orange, CRITICAL=red) | [x] |
| 5 | Install `mapbox-gl` and create `components/Map.tsx` wrapper with SSR disabled | [x] |
| 6 | Create `lib/api.ts` — typed fetch client that reads `NEXT_PUBLIC_API_URL` from env, handles errors | [x] |
| 7 | Configure `.env.local.example` with `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_MAPBOX_TOKEN` | [x] |
| 8 | Configure `vercel.json` for production deployment with correct env var references | [x] |

---

## Phase 12 — Public Frontend — Core Pages
> **Goal:** The public website is fully functional: map, state pages, alerts, disease alerts, user auth, and subscriptions all work end-to-end.
> **Prerequisite:** Phase 11 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Homepage — full-screen Nigeria Mapbox map with state polygons coloured by current risk level | [x] |
| 2 | Map — risk level legend overlay (LOW/MODERATE/HIGH/CRITICAL with colour swatches) | [x] |
| 3 | Map — clicking a state polygon navigates to `/states/{id}` | [x] |
| 4 | State list page (`/states`) — grid of all 37 states with risk level badge, sortable by risk | [x] |
| 5 | State detail page (`/states/{id}`) — risk level banner, latest advisory in selected language, government contacts | [x] |
| 6 | State detail — LGA vulnerability breakdown table sorted by score | [x] |
| 7 | State detail — health facilities section with mini-map and risk score badges | [x] |
| 8 | Active alerts banner — shown site-wide when any HIGH/CRITICAL alert exists, links to alert detail | [x] |
| 9 | Disease alerts page (`/disease-alerts`) — active NCDC/WHO AFRO alerts with disease name, level, and state | [x] |
| 10 | Alert history page (`/alerts/history`) — infinite scroll using cursor pagination | [x] |
| 11 | Auth pages — `/auth/register` and `/auth/login` with form validation, JWT stored in httpOnly cookie | [x] |
| 12 | Subscription management page (`/me/subscriptions`) — select states, toggle MODERATE/HIGH/CRITICAL notifications | [x] |

---

## Phase 13 — Public Frontend — i18n & Language Switcher
> **Goal:** Every user-facing string is translated into Hausa, Yoruba, and Igbo. The language switcher persists the user's choice. AI advisories render in the selected language from the DB.
> **Prerequisite:** Phase 12 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Build `LanguageSwitcher` component — dropdown with EN/HA/YO/IG, updates locale URL prefix | [x] |
| 2 | Complete Hausa translations in `messages/ha.json` for all UI strings defined in `en.json` | [x] |
| 3 | Complete Yoruba translations in `messages/yo.json` | [x] |
| 4 | Complete Igbo translations in `messages/ig.json` | [x] |
| 5 | State detail page — render the correct `advisory_{locale}` field from the API based on active locale | [x] |

---

## Phase 14 — Admin Panel — Setup
> **Goal:** The React 18 + Vite + TypeScript admin panel project is initialised, can authenticate against the backend, and has routing with protected pages.
> **Prerequisite:** Phase 10 complete (admin API routes live).

| # | Task | Status |
|---|------|:------:|
| 1 | Initialise project in `frontend-admin/` with Vite + React 18 + TypeScript template | [x] |
| 2 | Install and configure Tailwind CSS | [x] |
| 3 | Set up React Router v6 with protected route wrapper (redirects to `/login` if no valid JWT in `localStorage`) | [x] |
| 4 | Create `src/lib/api.ts` — typed API client that attaches `Authorization: Bearer {token}` header to every request | [x] |
| 5 | Configure `.env.example` with `VITE_API_URL` | [x] |
| 6 | Configure Render Static Site deployment — `render.yaml` with build command `npm run build` and publish dir `dist` | [x] |

---

## Phase 15 — Admin Panel — Features
> **Goal:** Admin users can see all state risk levels at a glance, trigger manual assessments, manage government contacts, and review historical logs.
> **Prerequisite:** Phase 14 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Login page — email/password form, calls `POST /api/auth/login`, stores JWT, redirects to dashboard | [x] |
| 2 | Dashboard (`/`) — grid of all 37 states with current risk level badge and last assessed timestamp | [x] |
| 3 | State detail modal/page — latest full assessment (all scores, all language advisories) | [x] |
| 4 | Manual trigger button on state detail — calls `POST /api/admin/trigger/{state_id}`, shows loading state | [x] |
| 5 | Government contacts page (`/contacts`) — table with inline edit and delete, `POST/PUT/DELETE` wired to API | [x] |
| 6 | Risk change logs page (`/logs`) — paginated table of all `RiskStateChange` records with from/to level and timestamp | [x] |
| 7 | Assessment history page (`/assessments`) — filterable by state, paginated, shows scores and risk level | [x] |
| 8 | Scheduler status page (`/scheduler`) — shows all 37 state jobs, current interval, and next run time | [x] |
| 9 | Protected routes — `require_admin` check via JWT role claim; non-admin JWT redirects to login | [x] |
| 10 | Logout — clears JWT from localStorage, redirects to login | [x] |

---

## Phase 16 — Testing & QA
> **Goal:** Core business logic is covered by automated tests. All API routes are tested. The full assessment pipeline can be run end-to-end in a test environment.
> **Prerequisite:** Phases 1-15 complete.

| # | Task | Status |
|---|------|:------:|
| 1 | Set up `pytest` with a test PostgreSQL database (separate `TEST_DATABASE_URL`), auto-apply migrations before test run | [ ] |
| 2 | Unit tests — AI engine: mock OpenAI API response, assert `RiskAssessmentResponse` validates correctly; assert invalid JSON raises `ValueError` | [ ] |
| 3 | Unit tests — scoring algorithms: LGA and facility weighted formulas, boundary values (0.0 and 100.0) | [ ] |
| 4 | Unit tests — auth: `hash_password` / `verify_password` round-trip; `create_access_token` / `decode_token` round-trip | [ ] |
| 5 | Unit tests — risk manager: transition logic, `get_consecutive_low_count`, scheduler downgrade threshold | [ ] |
| 6 | Integration tests — all 8 public API routes: assert status codes, response shapes, and cursor pagination | [ ] |
| 7 | Integration tests — auth routes: register → login → access protected → expired token → 401 | [ ] |
| 8 | Integration tests — admin routes: 403 for regular user, 401 for unauthenticated, correct data for admin | [ ] |
| 9 | End-to-end smoke test: run data pipeline → AI engine → risk manager → alert engine for Lagos; assert `risk_assessments` row, `risk_state_changes` row, and `active_alerts` row (if HIGH+) all exist | [ ] |

---

## Phase 17 — Deployment & Go-Live
> **Goal:** All three services are live in production, connected to the Supabase PostgreSQL instance, with all env vars set, migrations run, and the database seeded.
> **Prerequisite:** All previous phases complete and passing tests.

| # | Task | Status |
|---|------|:------:|
| 1 | Create Render Web Service for `backend/` — build command: `pip install -r requirements.txt`, start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | [ ] |
| 2 | Set all 6 production env vars on Render (`DATABASE_URL`, `OPENAI_API_KEY`, `RESEND_API_KEY`, `JWT_SECRET`, `MAPBOX_TOKEN`, `NOAA_TOKEN`) | [ ] |
| 3 | Run `alembic upgrade head` in production — confirm all 12 tables created on Supabase PostgreSQL | [ ] |
| 4 | Run all seed scripts in production (`seed_states.py`, `seed_admin.py`, `seed_government_contacts.py`) | [ ] |
| 5 | Create Vercel project for `frontend-public/` — link GitHub repo, set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_MAPBOX_TOKEN` | [ ] |
| 6 | Create Render Static Site for `frontend-admin/` — build `npm run build`, publish `dist/`, set `VITE_API_URL` | [ ] |
| 7 | Configure custom domain `climawatch.ng` — point DNS to Vercel (public site) and Render (admin subdomain) | [ ] |
| 8 | Run scheduler on first boot — confirm all 37 state jobs registered, trigger 3 manual assessments to verify full pipeline | [ ] |
| 9 | Final smoke test — visit public site, confirm map loads with live risk data; log into admin panel, trigger an assessment, confirm email dispatch | [ ] |

---

## Notes for Coding Assistants

- **Never** use Supabase SDK, Supabase Auth, or Supabase-specific SQL. `DATABASE_URL` is the only Supabase touchpoint.
- **Never** hardcode secrets — all keys come from environment variables.
- **Never** hardcode UI strings in JSX — all text goes through `next-intl` message files.
- **Never** use offset-based pagination — always cursor-based.
- **Never** change the AI model from `gpt-4o` without explicit instruction.
- **Never** introduce microservices — this is a modular monolith.
- **Always** store timestamps in UTC.
- **Always** use UUID primary keys.
- **Always** use `response_format={"type": "json_object"}` on every OpenAI call to guarantee parseable JSON.
- **Always** validate OpenAI JSON output against the `RiskAssessmentResponse` Pydantic schema before writing to DB.
- **Always** include the last 3 assessments + active disease alerts + facility summary in every OpenAI prompt.
- When a state's risk level is MODERATE or above, the scheduler **must** switch to the 2-hour cycle automatically.
- Admin accounts are **seeded only** — no self-registration for admin role.
