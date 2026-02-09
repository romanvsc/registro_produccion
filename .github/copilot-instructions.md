<!-- Copilot / AI agent instructions for the "registro_viajes" workspace -->

# Quick Orientations for AI Coding Agents

Purpose: help an AI agent be immediately productive in this repository by outlining the architecture, critical workflows, patterns, and concrete file examples.

1) Big-picture architecture
- Backend: FastAPI app (backend/main.py) using SQLAlchemy 2.0 models (backend/models.py) and MySQL via PyMySQL. DB connectivity is configured in backend/config.py; sessions come from backend/database.py (`get_db`).
- Frontend: Vue 3 + Vite PWA (frontend/). State with Pinia, IndexedDB via Dexie (frontend/src/services/db.js), and API client in frontend/src/services/api.js. Service worker registered in frontend/src/main.js.
- Offline sync: the frontend stores trips locally (IndexedDB) and calls POST /api/viajes/sync on the backend to persist records.
- Deployment/misc: api/index.py wraps the FastAPI app with Mangum for AWS Lambda compatibility.

2) High-value files to read first
- backend/main.py — application entry and router inclusion.
- backend/routes/viajes.py — sync logic; see `build_tablero_payload()` and the `/api/viajes/sync` handler (important: manual id fallback, validation, and CargaComb creation).
- backend/models.py — large `TableroProduccion` model; many NOT NULL columns and default handling in the route code.
- backend/config.py & backend/database.py — env-driven DB URL and `get_db()` session generator.
- frontend/src/main.js — service worker lifecycle hooks and update/reload behavior.
- frontend/src/views/ViajeView.vue — client-side validation patterns (parseKm, parseDecimal), computed guards (`canStartTrip`, `canCloseTrip`), and how UI maps to model fields.
- frontend/src/services/db.js & frontend/src/services/api.js — offline storage and sync calls (search these files for exact storage schemas).

3) Project-specific conventions & gotchas
- Pydantic v2 usage: route code uses `model_dump()` (v2) — expect Pydantic v2 semantics in schemas.
- Manual ID fallback: `TableroProduccion` insert code computes next id when DB rows lack AUTO_INCREMENT. If you change primary-key behavior, update insert logic in `viajes.py`.
- Decimal/date handling: some endpoints serialize Decimal/Date manually (see `get_viajes_por_chofer`) — avoid returning raw Decimal/Date objects from handlers.
- Commit/rollback pattern: route code frequently uses `db.add(...); db.commit(); db.refresh(...)` and `db.rollback()` on exceptions—follow the same transaction pattern.
- Fuel records: when a trip includes fuel, the backend creates a `CargaComb` record. If you modify trip fields (`combustible`, `remito`, `litros`), update that logic in `viajes.py`.

4) Developer workflows (commands you can run)
- Backend local dev:
  - create venv, copy `.env.example` → `.env`, edit credentials
  - install: `pip install -r backend/requirements.txt`
  - run: `python backend/main.py` (starts uvicorn with reload in the file)
  - helpers: `python backend/verify_db.py`, `python backend/verify_model.py`, `python backend/test_models.py`
- Frontend:
  - copy `.env.example` → `.env` inside `frontend/`
  - `cd frontend && npm install`
  - dev: `npm run dev`
  - build: `npm run build` and `npm run preview` to locally preview

5) When editing the schema or adding DB columns
- Update `backend/models.py` and keep SQLAlchemy types consistent.
- If introducing AUTO_INCREMENT changes, update insert fallback logic in `backend/routes/viajes.py`.
- Run `python backend/verify_model.py` and `python backend/test_models.py` locally; if the project uses Alembic add migration files and coordinate with ops.

6) Integration points to watch
- MySQL database (connection via `DATABASE_URL` in `backend/config.py`).
- Service Worker & PWA caching lifecycle (frontend/src/main.js) — changes to static assets must consider SW update/reload logic.
- AWS Lambda via `api/index.py` (Mangum) — keep API base path and handler lifespan in mind when modifying routes.

7) Example pointers for common tasks
- Add a new API route: create `backend/routes/yourroute.py`, export an `APIRouter(prefix="/api/yourroute")`, and include it in `backend/main.py` (app.include_router(...)).
- Fix sync validation: edit `build_tablero_payload()` in `backend/routes/viajes.py` (field normalization lives there) and keep response format matching `SyncResponse` in `schemas.py`.

8) Safety & testing notes for AI edits
- Do not change `TableroProduccion` column names lightly — many fields are assumed by frontend and the fuel-registration logic.
- Use existing helper scripts (`verify_db.py`, `verify_model.py`, `test_models.py`) after model or DB changes.
- Preserve manual serialization for Decimal/datetime in routes unless you update all callers.

If anything here is unclear or you want examples expanded (e.g., exact IndexedDB schema or Pydantic schemas), tell me which area to expand and I will iterate.
