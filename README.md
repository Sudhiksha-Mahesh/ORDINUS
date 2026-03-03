# Ordinus – Intelligent Academic Timetable Generator

Foundational version of an AI-ready academic timetable generator with PostgreSQL, FastAPI, and React.

## Stack

- **Backend:** Python 3.11+, FastAPI (async), SQLAlchemy (async), PostgreSQL, Alembic
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS

## Quick start

### 1. Database

**Option A: Neon (recommended – no local PostgreSQL needed)**

1. Sign up at [neon.tech](https://neon.tech) and create a project.
2. In the Neon dashboard, open **Connection string** and copy the URI (e.g. “Pooled connection” or “Direct”).
3. It will look like:  
   `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
   
4. For this app, change the scheme to use the async driver:  
   `postgresql**+asyncpg**://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
5. Put that in `backend/.env` as `DATABASE_URL=...`

**Option B: Local PostgreSQL**

```bash
createdb ordinus
# In backend/.env: DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ordinus
```

Copy env and set `DATABASE_URL`:

```bash
cd backend
cp .env.example .env
# Edit .env with your DATABASE_URL (Neon or local)
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Run from the `backend` directory so that `core` and `models` resolve. API: http://localhost:8000

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173. The dev server proxies `/api` to the backend.

## Project layout

```
backend/
  core/         config, database
  models/        SQLAlchemy models
  schemas/       Pydantic schemas
  services/      business logic (incl. backtracking scheduler)
  routers/       FastAPI endpoints
  alembic/       migrations
  main.py
frontend/
  src/
    components/  Layout, shared UI
    pages/       Dashboard, Faculty, Class, Subject, Generate, View Timetable
    services/    api client
  ...
```

## Features

- **Faculty:** Add, edit, delete; set availability (day + slot).
- **Classes:** Add classes with working days and slots per day.
- **Subjects:** Add subjects, assign faculty; assign subjects to classes with hours per week.
- **Timetable:** Generate via CSP-style backtracking (no faculty clash, weekly hours satisfied); view grid (rows = days, columns = slots).

## Timetable generation

The scheduler in `services/scheduler.py` uses backtracking to fill a (days × slots) grid so that:

- Each subject gets its required hours per week.
- Faculty are only placed in slots where they are available (from faculty availability).

Designed to be extended later with heuristics or AI.
