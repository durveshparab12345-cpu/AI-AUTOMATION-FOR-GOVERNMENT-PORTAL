"""Auth request/response schemas."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    organization_id: uuid.UUID
    user_email: str
    user_name: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    organization_id: uuid.UUID
    is_active: bool

    model_config = {"from_attributes": True}
