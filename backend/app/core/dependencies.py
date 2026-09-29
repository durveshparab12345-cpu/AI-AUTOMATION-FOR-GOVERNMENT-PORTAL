"""
Shared FastAPI dependency functions.

These are used across multiple route modules to enforce authentication
and organization isolation.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    """Decode the JWT and return its payload. Raises 401 if invalid."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if not payload.get("sub"):
            raise credentials_exc
        return payload
    except JWTError as exc:
        raise credentials_exc from exc


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
