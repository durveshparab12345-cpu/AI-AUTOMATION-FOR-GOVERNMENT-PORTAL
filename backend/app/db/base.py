"""
SQLAlchemy declarative base.

All ORM model classes must inherit from `Base`.  Importing this module in
`app/db/session.py` (and in the Alembic env.py) ensures that every model is
registered with the metadata object used for migrations.

No application models are defined here — this module exists purely to own the
shared `Base` and `metadata` objects.

Future stages will import `Base` from here:
    from app.db.base import Base

    class Company(Base):
        __tablename__ = "companies"
        ...
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    Placing all models under a single Base gives Alembic a single source of
    truth for auto-generating migrations via `autogenerate`.
    """
