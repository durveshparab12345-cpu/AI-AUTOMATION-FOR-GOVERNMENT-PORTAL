"""
Authentication routes — POST /api/v1/auth/token and /register.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate with email + password.
    Returns a signed JWT access token containing organization_id.
    """
    repo = UserRepository(db)
    user = await repo.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        subject=user.email,
        extra={"tenant_id": str(user.tenant_id), "user_id": str(user.id)},
    )
    return TokenResponse(
        access_token=token,
        organization_id=user.tenant_id,
        user_email=user.email,
        user_name=user.full_name,
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Register a new organization + admin user."""
    repo = UserRepository(db)

    # Check email not already taken
    existing = await repo.get_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    import re

    slug = re.sub(r"[^a-z0-9]+", "-", payload.organization_name.lower()).strip("-")

    _, user = await repo.create_org_and_user(
        org_name=payload.organization_name,
        org_slug=slug,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    return UserRead.model_validate(user)
