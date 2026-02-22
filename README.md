# Job Tracker

Central panel to track job applications from multiple sites. **Backend** (FastAPI) and **frontend** (Next.js + Mantine) live in separate folders and can be run or deployed independently.

---

## Demo

**[Try the live app →](https://job-tracker-orcin-iota-85.vercel.app/)**

---

## Run locally

You need **PostgreSQL** running, then the **backend**, then the **frontend** (two terminals).

### 1. Start PostgreSQL

**Option A — local Postgres**

Create the database (adjust user/password if needed):

```bash
createdb jobtracker
```

Default URL: `postgresql://postgres:postgres@localhost:5432/jobtracker`.

**Option B — Docker (Postgres only)**

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
# Edit .env if needed: DATABASE_URL, JWT_SECRET, ADMIN_EMAILS (for dev login)
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### 3. Frontend (terminal 2)

```bash
cd app
npm install
cp .env.local.example .env.local    # set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

- App: http://localhost:3000  

### 4. Use the app

- Open http://localhost:3000 — you’re redirected to `/dashboard` or `/login`.
- **Dev login:** Set `ADMIN_EMAILS=your@email.com` in `backend/.env`, then use **Dev login (no OAuth)** on the login page.
- **Dashboard:** Upcoming interviews; click one to open the application.
- **Applications:** List, filter, search; **Add application** → paste job URL (title/company fetched) → set applied date.
- **Application detail:** View/edit status and notes; add interview sessions (name + date).
- **Admin** (users with `is_admin`): Settings (site name, maintenance), Users (list, set admin/active).

---

## OAuth (production)

Keep secrets only in `backend/.env` (never commit real values). Use `backend/.env.example` as a template.

- **Google:** Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. In Google Cloud Console add redirect URI: `http://localhost:8000/api/auth/callback` (or `BACKEND_ORIGIN` + `/api/auth/callback`).
- **LinkedIn:** Set `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`. In LinkedIn Developer Portal add the same redirect URI.

---

## Docker

From the project root:

```bash
docker compose up --build
```

Optional: set `ADMIN_EMAILS` (and other env) in `.env` or export before running.

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000 — Docs: http://localhost:8000/docs  

PostgreSQL data is stored in the `postgres_data` volume.

---

## Project layout

| Folder      | Stack              | Description |
|------------|--------------------|-------------|
| **`backend/`** | FastAPI, SQLAlchemy, Alembic | API: auth (JWT + Google/LinkedIn OAuth), applications CRUD, job URL fetch, dashboard, admin. Run with `uvicorn`. |
| **`app/`**     | Next.js 14, Mantine 7 | Web app: dashboard, applications, application detail, admin (settings, users). Uses `NEXT_PUBLIC_API_URL` for the API. |

Backend and frontend can be developed or deployed separately.
