# ClimaWatch — development Makefile
# Requires: GNU make, Python 3.12+, Node 18+, uvicorn, npm
#
# Usage:
#   make dev              Start all three services in parallel
#   make backend          Backend only  (http://localhost:8000)
#   make public           Public site only (http://localhost:3000)
#   make admin            Admin panel only (http://localhost:5173)
#   make install          Install all dependencies
#   make migrate          Run Alembic migrations
#   make seed             Seed states, admin account, and government contacts
#   make test             Run the backend test suite (no E2E)
#   make test-e2e         Run the end-to-end smoke test (requires E2E=1 env)

.PHONY: dev backend public admin install install-backend install-public install-admin \
        migrate seed test test-e2e

# ── Parallel dev stack ────────────────────────────────────────────────────────
dev:
	@echo ""
	@echo "  ClimaWatch dev stack"
	@echo "  ─────────────────────────────────────────────"
	@echo "  Backend API   →  http://localhost:8000"
	@echo "  Public site   →  http://localhost:3000"
	@echo "  Admin panel   →  http://localhost:5173"
	@echo "  ─────────────────────────────────────────────"
	@echo "  Press Ctrl+C to stop all services"
	@echo ""
	@(cd backend && uvicorn app.main:app --reload --port 8000) & \
	 (cd frontend-public && npm run dev) & \
	 (cd frontend-admin && npm run dev) & \
	 wait

# ── Individual services ───────────────────────────────────────────────────────
backend:
	cd backend && uvicorn app.main:app --reload --port 8000

public:
	cd frontend-public && npm run dev

admin:
	cd frontend-admin && npm run dev

# ── Install dependencies ──────────────────────────────────────────────────────
install: install-backend install-public install-admin
	@echo "All dependencies installed."

install-backend:
	cd backend && pip install -r requirements.txt

install-public:
	cd frontend-public && npm install

install-admin:
	cd frontend-admin && npm install

# ── Database ──────────────────────────────────────────────────────────────────
migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python scripts/seed_states.py
	cd backend && python scripts/seed_admin.py
	cd backend && python scripts/seed_government_contacts.py

# ── Tests ─────────────────────────────────────────────────────────────────────
test:
	cd backend && python -m pytest tests/ -m "not e2e" -q

test-e2e:
	cd backend && E2E=1 python -m pytest tests/test_e2e.py -v
