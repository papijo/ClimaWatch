# ClimaWatch — Claude Code Project Memory

## What this project is

ClimaWatch is an open-source, AI-powered climate-health intelligence platform for Nigeria. It ingests open climate data, generates AI-powered health risk assessments for all 36 Nigerian states and FCT, maps health facility vulnerability against climate risk, and delivers early warnings through a public website and email alert system.

Built for the UNICEF Climate Ventures Programme (Areas 1, 2 & 3).
Owned and built by Serge Ltd — Jonathan Ebhota & Ehi Ero-Omoighe.

---

## Architecture — read this before touching any file

ClimaWatch is a **modular monolith**. One codebase. One deployment unit per service. No microservices.

```
climawatch/
  backend/          # Python 3.12 + FastAPI (deployed on Render)
  frontend-public/  # NextJS 14 App Router (deployed on Vercel)
  frontend-admin/   # React 18 + Vite + TypeScript (deployed on Render)
  docker-compose.yml
  .env.example
  CLAUDE.md
```

### Backend module structure

```
backend/app/modules/
  data_pipeline/        # Fetches Open-Meteo, NASA POWER, NOAA CDO + ingests NHFR/NCDC/WHO AFRO
  scheduler/            # APScheduler — 12hr default, 2-3hr when state is MODERATE or above
  ai_engine/            # OpenAI API prompts per state, parses structured JSON response
  vulnerability_scoring/ # LGA-level and health facility risk scores
  risk_manager/         # State risk transitions, history logging
  alert_engine/         # Website active_alerts + Resend email dispatch
  api/                  # FastAPI route handlers (public, user, admin)
  auth/                 # JWT + bcrypt — NO Supabase Auth
```

---

## Tech stack

| Layer          | Technology                                        |
| -------------- | ------------------------------------------------- |
| Backend        | Python 3.12 + FastAPI                             |
| Public website | NextJS 14 (App Router)                            |
| Admin panel    | React 18 + Vite + TypeScript                      |
| Database       | PostgreSQL — connected via Supabase (portable)    |
| ORM            | SQLAlchemy + Alembic                              |
| AI engine      | OpenAI API (gpt-4o)                               |
| Maps           | Mapbox GL JS                                      |
| Email          | Resend (sender: hello@weareserge.com)             |
| Scheduler      | APScheduler (in-process, inside FastAPI)          |
| Auth           | JWT (python-jose) + bcrypt — no external provider |
| i18n           | next-intl — EN, HA, YO, IG                        |
| HTTP client    | httpx (async)                                     |
| Validation     | Pydantic v2                                       |

---

## Build & run commands

### Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head          # run migrations
uvicorn app.main:app --reload # local dev
```

### Frontend public

```bash
cd frontend-public
npm install
npm run dev
npm run build
```

### Frontend admin

```bash
cd frontend-admin
npm install
npm run dev
npm run build
```

### Full local environment

```bash
docker-compose up   # starts backend + postgres
```

### Database migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1
```

---

## Critical rules — always follow these

### Database portability (non-negotiable)

- Connect to PostgreSQL using a standard SQLAlchemy connection string ONLY
- NEVER use the Supabase Python SDK, Supabase Auth, Supabase Realtime, or Supabase Storage
- NEVER use Supabase-specific SQL extensions or RLS policies
- The only Supabase touch point is the DATABASE_URL environment variable
- Changing DATABASE_URL must be the ONLY step needed to migrate to any other PostgreSQL host

### Secrets — never hardcode

- All secrets live in environment variables
- Use `.env` locally, Render/Vercel environment settings in production
- Never commit `.env` files — `.env.example` contains keys with empty values only
- Required env vars: `DATABASE_URL`, `OPENAI_API_KEY`, `RESEND_API_KEY`, `JWT_SECRET`, `MAPBOX_TOKEN`, `NOAA_TOKEN`

### AI engine

- Model: `gpt-4o` — do not change this without instruction
- Always use `response_format={"type": "json_object"}` to guarantee valid JSON output
- Always send structured prompts that request a JSON response
- Always validate the JSON response against the RiskAssessment Pydantic schema before writing to DB
- Include the last 3 assessments in prompt context for trend awareness
- Include active disease alerts and facility data in every state prompt

### Auth

- Public registered users and Serge admin both use JWT
- Passwords hashed with bcrypt — never store plaintext
- Admin accounts are seeded directly in DB — no self-registration for admin
- Admin role is checked on the JWT payload for every admin route

### i18n

- Every UI string in frontend-public lives in a messages file — never hardcoded in JSX
- Files: `frontend-public/messages/en.json`, `ha.json`, `yo.json`, `ig.json`
- AI advisories are stored per language in the DB (advisory_en, advisory_ha, advisory_yo, advisory_ig)
- Adding a new language = new messages JSON file only, zero code changes

### Adaptive scheduler

- Default cycle: every 12 hours for all 37 locations
- If a state's risk level is MODERATE or above → switch to 2-3 hour cycle automatically
- If a state returns to LOW for two consecutive cycles → return to 12-hour cycle
- Scheduler runs inside FastAPI as an APScheduler in-process background task

---

## Data sources

| Source            | Type              | Update frequency | Key                |
| ----------------- | ----------------- | ---------------- | ------------------ |
| Open-Meteo        | Live API          | Hourly           | None required      |
| NASA POWER        | Live API          | Daily            | None required      |
| NOAA CDO          | Live API          | Weekly           | Token (NOAA_TOKEN) |
| NHFR via HDX      | Dataset ingestion | Monthly          | Free download      |
| NCDC Data Portal  | Dataset ingestion | Weekly           | Free download      |
| WHO AFRO Bulletin | Parsed report     | Weekly           | Free               |

---

## Database tables (reference)

**Existing:** `states`, `climate_readings`, `risk_assessments`, `risk_state_changes`, `active_alerts`, `government_contacts`, `users`, `user_subscriptions`

**v2 additions:** `health_facilities`, `facility_risk_scores`, `lga_vulnerability_scores`, `disease_alerts`

All tables use UUID primary keys. All timestamps are stored in UTC.

---

## API structure (reference)

**Public (no auth):**

- `GET /api/states` — all 37 states with current risk level
- `GET /api/states/{state_id}` — full state detail
- `GET /api/states/{state_id}/lgas` — LGA breakdown
- `GET /api/facilities` — health facilities with risk scores
- `GET /api/alerts/active` — active HIGH/CRITICAL alerts
- `GET /api/alerts/history` — paginated alert history
- `GET /api/disease-alerts` — active NCDC/WHO alerts
- `GET /api/forecasts/{state_id}` — disease and surge forecasts

**Authenticated (JWT):**

- `POST /api/auth/register`, `POST /api/auth/login`
- `GET/POST /api/me/subscriptions`

**Admin (JWT + admin role):**

- `POST/PUT/DELETE /api/admin/contacts`
- `GET /api/admin/logs`
- `GET /api/admin/assessments`
- `POST /api/admin/trigger/{state_id}` — manual assessment trigger

---

## Deployment (reference)

| Service            | Platform           | Notes                            |
| ------------------ | ------------------ | -------------------------------- |
| FastAPI backend    | Render Web Service | Always-on, auto-deploy from main |
| NextJS public site | Vercel             | Auto-deploy from main            |
| React admin panel  | Render Static Site | Auto-deploy from main            |
| PostgreSQL         | Supabase           | Standard connection string only  |

---

## What NOT to do

- Do not introduce microservices — this is and will remain a modular monolith until explicitly instructed otherwise
- Do not add Supabase SDK imports anywhere
- Do not hardcode any language strings in JSX — always use next-intl
- Do not change the AI model without instruction
- Do not add authentication middleware to public API routes
- Do not create admin accounts via any registration flow — seed only
- Do not use offset-based pagination — use cursor-based pagination for all list endpoints
