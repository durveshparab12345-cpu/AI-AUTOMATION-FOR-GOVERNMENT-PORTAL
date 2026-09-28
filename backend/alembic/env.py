"""
Alembic environment configuration.

Wired to the application's async SQLAlchemy engine and ORM models so that
`alembic revision --autogenerate` can detect schema changes automatically.

Important:
  - DATABASE_URL is read from the application's Settings (environment variable).
  - All model modules must be imported here (or via app.db.base) before
    `target_metadata` is referenced, so that their tables are registered.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Load application configuration so DATABASE_URL is resolved from env vars.
# ---------------------------------------------------------------------------
from app.core.config import settings

# ---------------------------------------------------------------------------
# Import Base — which will also import all models that register with it.
# Add future model imports here as new models are created in later stages:
#
#   from app.models import company, user, portal, workflow, ...
#
# Importing Base alone is sufficient for Stage 1 (no tables yet).
# ---------------------------------------------------------------------------
from app.db.base import Base

# Alembic Config object — gives access to values in alembic.ini.
config = context.config

# Override the sqlalchemy.url from alembic.ini with the application setting.
# This ensures a single source of truth for the database connection string.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging if present.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object used by `autogenerate` to detect schema differences.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL scripts without requiring a live database connection.
    Useful for reviewing migrations before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations using an async engine.

    asyncpg requires an async engine; this function creates a disposable
    engine purely for the migration run and disposes it immediately after.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
