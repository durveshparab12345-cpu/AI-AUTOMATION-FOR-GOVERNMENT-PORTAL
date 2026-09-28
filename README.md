# AI Portal Automation Platform

## What Is This?

The **AI Portal Automation Platform** is a production-oriented SaaS platform that allows authorized business users to:

1. Explain or record how a government or business portal is used.
2. Define company-specific business rules.
3. Execute repetitive workflows through controlled, supervised browser automation with minimum manual intervention.

The platform is designed for regulated, authorized use cases — not for defeating portal security controls.

---

## Long-Term Product Vision

- Multi-tenant: support multiple companies, each with their own portals, rules, and users.
- Workflow recording: a business user describes or demonstrates a workflow; the system structures it into versioned, reusable data.
- AI-assisted reasoning: an LLM layer interprets workflow steps and validates outputs — but never takes unsupervised critical action.
- Human approval gates: sensitive actions require human confirmation before execution.
- Full audit trail: every action is logged for compliance and review.
- First target domain: healthcare portal workflows (e.g., PM-JAY-related hospital operations) — **not yet implemented**.

---

## Current Scope: Stage 1 — System Foundation

Stage 1 establishes only the project foundation:

- Clean repository structure
- FastAPI backend with a health endpoint
- PostgreSQL / SQLAlchemy / Alembic foundation (no application tables yet)
- React + TypeScript + Vite frontend scaffold
- Centralized environment-variable-based configuration
- Basic test coverage for the health endpoint
- Code quality tooling (Ruff, Black, pytest)
- Documentation structure

**Nothing in Stage 1 performs automation, connects to portals, or involves AI.**

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.12+, FastAPI, Uvicorn |
| Data validation | Pydantic v2 |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Database | PostgreSQL |
| Frontend | React, TypeScript, Vite |
| Testing | pytest, pytest-asyncio, httpx |
| Linting | Ruff |
| Formatting | Black |
| Future: browser automation | Playwright (not yet) |
| Future: background tasks | Celery + Redis (not yet) |
| Future: AI reasoning | LLM API (not yet) |

---

## Repository Structure

```
ai-portal-automation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application factory
│   │   ├── core/
│   │   │   ├── config.py        # Centralized settings (env vars)
│   │   │   └── logging.py       # Structured logging setup
│   │   ├── api/v1/
│   │   │   └── health.py        # GET /api/v1/health
│   │   ├── db/
│   │   │   ├── base.py          # SQLAlchemy declarative base
│   │   │   └── session.py       # Async engine + session factory
│   │   ├── models/              # ORM models (populated in future stages)
│   │   ├── schemas/             # Pydantic schemas (populated in future stages)
│   │   ├── services/            # Business logic services
│   │   └── repositories/        # Data access layer
│   ├── tests/
│   │   └── test_health.py
│   ├── alembic/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── hooks/
│   │   └── layouts/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   ├── architecture/README.md
│   ├── development/README.md
│   ├── workflows/README.md
│   └── security/README.md
├── .env.example
├── .gitignore
└── README.md
```

---

## How to Run the Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp ../.env.example .env
# Edit .env with your local database URL and secret key

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API is available at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

---

## How to Run the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend is available at: http://localhost:5173

---

## How to Run Tests

```bash
cd backend

# Activate your virtual environment first
pip install -r requirements-dev.txt

pytest
```

---

## How Environment Variables Work

All configuration is driven by environment variables. See `.env.example` for the full reference.

- Copy `.env.example` → `.env` inside the `backend/` directory (or at repo root).
- The `.env` file is **git-ignored** and must never be committed.
- `backend/app/core/config.py` loads all settings via Pydantic `BaseSettings`.
- Sensitive defaults are never provided — the application will fail fast if required secrets are missing in non-development environments.

---

## What Is Intentionally NOT Implemented Yet

- Browser automation (Playwright)
- AI/LLM reasoning layer
- Workflow recording or execution engine
- Portal connections of any kind
- PM-JAY or any healthcare-specific workflows
- Authentication and authorization
- Multi-tenant company/user management
- Background task workers (Celery/Redis)
- Production deployment configuration
- Dashboard or any real UI beyond the foundation page
