"""
Async database engine and session factory.

This module provides:
    - `engine`         — the shared SQLAlchemy async engine
    - `AsyncSessionLocal` — the async session factory
    - `get_db`         — a FastAPI dependency that yields a scoped session

The engine is created lazily on first import.  No connection is attempted
until an actual database operation is performed, which allows the application
to start even when the database is temporarily unavailable (useful in tests).

Usage in a route:
    from app.db.session import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(SomeModel))
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# ---------------------------------------------------------------------------
# Engine
# pool_pre_ping=True: validates connections before use, handles stale
#   connections gracefully (important for long-running services).
# echo=False: set to True locally if you want to see raw SQL in the logs,
#   but leave False for production to avoid credential leakage in logs.
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# ---------------------------------------------------------------------------
# Session factory
# expire_on_commit=False: keeps attributes accessible after commit without
#   requiring an additional round-trip to the database.
# ---------------------------------------------------------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.

    The session is automatically closed when the request completes,
    whether it succeeds or raises an exception.
    """
    async with AsyncSessionLocal() as session:
        yield session
