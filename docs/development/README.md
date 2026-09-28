# Development Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Git

## Initial Setup

### 1. Clone and enter the repository

```bash
git clone <repo-url>
cd ai-portal-automation
```

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install all dependencies
pip install -r requirements-dev.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your local DATABASE_URL and SECRET_KEY
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

---

## Running the Backend

```bash
cd backend
.venv\Scripts\activate   # or source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running the Frontend

```bash
cd frontend
npm run dev
```

- Frontend: http://localhost:5173

---

## Running Tests

```bash
cd backend
.venv\Scripts\activate
pytest -v
```

---

## Code Quality

```bash
cd backend
.venv\Scripts\activate

# Lint (check only)
ruff check app/ tests/

# Lint (auto-fix)
ruff check app/ tests/ --fix

# Format (check only)
black app/ tests/ --check

# Format (apply)
black app/ tests/
```

---

## Database Migrations (Alembic)

```bash
cd backend
.venv\Scripts\activate

# Apply all pending migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe_change"

# Check current migration state
alembic current
```

---

## Development Conventions

### Python

- Line length: 100 characters (Ruff + Black)
- Target: Python 3.12+
- Async: all DB operations use async SQLAlchemy
- No business logic in route files
- No raw SQL — use SQLAlchemy ORM or Core expressions
- All secrets from environment variables — never hard-coded

### TypeScript/React

- Strict TypeScript mode enabled
- Component files: PascalCase (e.g., `WorkflowCard.tsx`)
- Utility/hook files: camelCase (e.g., `useWorkflowStatus.ts`)
- No `any` types

### Git

- Branch naming: `feature/short-description`, `fix/short-description`
- Never commit to `main` directly
- Never commit `.env` files
- Write meaningful commit messages

---

## Stage-by-Stage Development Rules

Each stage builds on the previous one. **Do not skip stages or implement
features belonging to a future stage.**

| Stage | Scope |
|---|---|
| Stage 1 | Repository foundation, health endpoint, DB layer, frontend scaffold |
| Stage 2 | Authentication, company/user management, RBAC |
| Stage 3 | Portal management, encrypted credential storage |
| Stage 4 | Workflow definitions and versioning |
| Stage 5 | Workflow execution engine |
| Stage 6 | AI reasoning integration |
| Stage 7 | Browser automation (Playwright) |
| Stage 8 | Production hardening, monitoring, deployment |
