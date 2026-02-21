# Job Tracker

Central panel to track job applications from multiple sites. **Backend** (FastAPI) and **frontend** (Next.js + Mantine) are in separate folders and can be run or deployed independently.

## Run locally

You need **PostgreSQL** running, then the **backend**, then the **frontend** (in two terminals).

### 1. Start PostgreSQL

- **Option A — installed on your machine:** start the Postgres service and create a database:
  ```bash
  createdb jobtracker
  ```
  Default URL: `postgresql://postgres:postgres@localhost:5432/jobtracker` (adjust user/password if different).

- **Option B — run only Postgres in Docker:**
  ```bash
  docker run -d --name jobtracker-db -p 5432:5432 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=jobtracker \
    postgres:16-alpine
  ```

### 2. Backend (terminal 1)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed: DATABASE_URL (default above), JWT_SECRET, ADMIN_EMAILS for dev login
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### 3. Frontend (terminal 2)

```bash
cd frontend
npm install                        # or: bun install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                        # or: bun run dev
```

- App: http://localhost:3000  

### 4. Use the app

- Open http://localhost:3000 — you are redirected to `/dashboard` or `/login`.
- **Dev login**: Set `ADMIN_EMAILS=your@email.com` in `backend/.env`, then use **Dev login (no OAuth)** on the login page.
- **Dashboard**: Shows your next upcoming interviews; click one to open the application detail.
- **Applications**: List, filter, search. "Add application" → paste job URL (we fetch title/company) → set applied date.
- **Application detail**: View/edit status and notes; add interview sessions (name + date).
- **Admin** (only for users with `is_admin`): Settings (site name, maintenance mode), Users (list, set admin/active).

## OAuth (production)

**Keep secrets only in `backend/.env`** (never commit real values to the repo). Use `backend/.env.example` as a template.

- **Google**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `backend/.env`. Add redirect URI `http://localhost:8000/api/auth/callback` (or your `BACKEND_ORIGIN` + `/api/auth/callback`) in Google Cloud Console.
- **LinkedIn**: Set `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` in `backend/.env`; add the same redirect URI in LinkedIn Developer Portal.

## Docker

From the project root:

```bash
# Build and run
docker compose up --build

# Optional: set ADMIN_EMAILS for dev login (and other env in .env or export)
export ADMIN_EMAILS=dev@example.com
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000 — Docs: http://localhost:8000/docs  

PostgreSQL data is stored in a Docker volume `postgres_data`.

## Project layout

- **`backend/`** — FastAPI app, SQLAlchemy, Alembic, auth (JWT + OAuth), applications CRUD, job URL fetch, dashboard, admin. Run on its own with `uvicorn`; no frontend required for API usage.
- **`frontend/`** — Next.js 14 + Mantine 7; user panel (dashboard, applications) and admin panel (settings, users). Points at the API via `NEXT_PUBLIC_API_URL` (e.g. `http://localhost:8000`).

You can develop or deploy each part separately: run only the backend for API access, or only the frontend (with an existing API URL).
