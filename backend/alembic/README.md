# Alembic — Database Migrations

This directory will contain Alembic migration scripts once application-level
database tables are introduced (Stage 2+).

---

## Setup

Alembic is initialized with async support.  The configuration in
`alembic.ini` and `env.py` is wired to:

- Load `DATABASE_URL` from the application's environment settings.
- Import all ORM models via `app.db.base` so that `autogenerate` can detect
  schema changes automatically.

---

## Creating a Migration

```bash
cd backend

# Activate your virtual environment first.

# Auto-generate a migration after changing ORM models:
alembic revision --autogenerate -m "describe_what_changed"

# Review the generated file in alembic/versions/ before applying it.
```

---

## Applying Migrations

```bash
# Apply all pending migrations to the database:
alembic upgrade head

# Downgrade one step:
alembic downgrade -1

# Show current migration state:
alembic current

# Show migration history:
alembic history --verbose
```

---

## Why No Migrations Exist Yet

Stage 1 defines no application tables.  The declarative `Base` exists and
is wired to Alembic, but there are no models registered with it yet.

Migrations will be created in Stage 2 when the first domain models
(companies, users, portals, etc.) are introduced.

---

## Important Rules

- Always review auto-generated migrations before applying them.
- Never edit the `down_revision` field of an existing migration.
- Do not delete migration files from `versions/` — they form a linked history.
- The `versions/` directory is tracked in Git so the migration history is shared across the team.
