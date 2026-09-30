"""UserRepository — user and organization data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.email == email, User.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_org_by_id(self, org_id: uuid.UUID) -> Organization | None:
        result = await self._db.execute(select(Organization).where(Organization.id == org_id))
        return result.scalar_one_or_none()

    async def create_org_and_user(
        self,
        org_name: str,
        org_slug: str,
        email: str,
        hashed_password: str,
        full_name: str,
    ) -> tuple[Organization, User]:
        org = Organization(id=uuid.uuid4(), name=org_name, slug=org_slug)
        self._db.add(org)
        await self._db.flush()
        
        # Split full_name into first_name and last_name
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else None
        
        user = User(
            id=uuid.uuid4(),
            tenant_id=org.id,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_admin=True,
        )
        self._db.add(user)
        await self._db.commit()
        await self._db.refresh(user)
        return org, user
