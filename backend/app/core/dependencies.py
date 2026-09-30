"""
Shared FastAPI dependency functions.

These are used across multiple route modules to enforce authentication
and organization isolation.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import AsyncSessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_db() -> AsyncSession:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """Decode the JWT and return its payload. Raises 401 if invalid."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if not payload or not payload.get("sub"):
        raise credentials_exc
    return payload


async def get_current_org_id(
    payload: dict = Depends(get_current_user_payload),
) -> uuid.UUID:
    """Extract and return the organization_id from the JWT payload."""
    org_id = payload.get("organization_id")
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing organization context",
        )
    return uuid.UUID(org_id)


async def get_current_user_email(
    payload: dict = Depends(get_current_user_payload),
) -> str:
    """Return the authenticated user's email from the JWT payload."""
    return payload["sub"]


async def get_current_user(
    email: str = Depends(get_current_user_email),
    db: AsyncSession = Depends(get_db),
) -> "User":
    """Get the current authenticated user from the database."""
    from app.models.user import User
    from sqlalchemy.future import select

    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
