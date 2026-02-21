# Job Tracker API

FastAPI backend for the job tracker. Uses **PostgreSQL** for the database.

## Setup

1. Run PostgreSQL (e.g. locally on port 5432 or via Docker: `docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=jobtracker postgres:16-alpine`).

2. In the backend folder:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set DATABASE_URL if needed (default: postgresql://postgres:postgres@localhost:5432/jobtracker), JWT_SECRET, and ADMIN_EMAILS for dev login
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Dev login

If `ADMIN_EMAILS` is set in `.env` (e.g. `ADMIN_EMAILS=dev@example.com`), you can use "Dev login (no OAuth)" on the frontend login page to get a JWT without configuring Google/LinkedIn.

## OAuth

- **Google**: Create credentials at Google Cloud Console, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. Add redirect URI `http://localhost:8000/api/auth/callback` (or your `BACKEND_ORIGIN` + `/api/auth/callback`).
- **LinkedIn**: Create an app at LinkedIn Developer Portal, set `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`. Add redirect URI same as above.

## API docs

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
