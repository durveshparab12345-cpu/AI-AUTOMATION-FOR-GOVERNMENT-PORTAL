"""
CaseRepository — data access for Case model.

Handles case-specific queries like:
  - Finding cases by status
  - Finding cases by beneficiary
  - Case timeline queries
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import and_, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.case import Case
from app.repositories.base import BaseRepository


class CaseRepository(BaseRepository[Case]):
    """Repository for Case model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Case)

    async def get_with_relations(
        self,
        id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Case | None:
        """Get a case with beneficiary and user relations loaded."""
        stmt = (
            select(Case)
            .where(and_(Case.id == id, Case.organization_id == organization_id))
            .options(
                selectinload(Case.beneficiary),
                selectinload(Case.created_user),
                selectinload(Case.updated_user),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reference(
        self,
        case_reference: str,
        organization_id: uuid.UUID,
    ) -> Case | None:
        """Get a case by its reference number."""
        stmt = select(Case).where(
            and_(
                Case.case_reference == case_reference,
                Case.organization_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_beneficiary(
        self,
        beneficiary_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Case], int]:
        """List all cases for a beneficiary."""
        # Count
        from sqlalchemy import count
        count_result = await self.session.execute(
            select(count(Case.id)).where(
                and_(
                    Case.beneficiary_id == beneficiary_id,
                    Case.organization_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Case)
            .where(
                and_(
                    Case.beneficiary_id == beneficiary_id,
                    Case.organization_id == organization_id,
                )
            )
            .order_by(desc(Case.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        return cases, total

    async def list_by_status(
        self,
        status: str,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Case], int]:
        """List all cases with a specific status."""
        from sqlalchemy import count
        # Count
        count_result = await self.session.execute(
            select(count(Case.id)).where(
                and_(
                    Case.status == status,
                    Case.organization_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Case)
            .where(
                and_(
                    Case.status == status,
                    Case.organization_id == organization_id,
                )
            )
            .order_by(desc(Case.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        return cases, total

    async def list_by_hospital(
        self,
        hospital_code: str,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Case], int]:
        """List all cases for a specific hospital."""
        from sqlalchemy import count
        # Count
        count_result = await self.session.execute(
            select(count(Case.id)).where(
                and_(
                    Case.hospital_code == hospital_code,
                    Case.organization_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Case)
            .where(
                and_(
                    Case.hospital_code == hospital_code,
                    Case.organization_id == organization_id,
                )
            )
            .order_by(desc(Case.admission_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        return cases, total

    async def list_by_admission_date_range(
        self,
        organization_id: uuid.UUID,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Case], int]:
        """List cases admitted within a date range."""
        from sqlalchemy import count
        # Count
        count_result = await self.session.execute(
            select(count(Case.id)).where(
                and_(
                    Case.organization_id == organization_id,
                    Case.admission_date >= start_date,
                    Case.admission_date <= end_date,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Case)
            .where(
                and_(
                    Case.organization_id == organization_id,
                    Case.admission_date >= start_date,
                    Case.admission_date <= end_date,
                )
            )
            .order_by(desc(Case.admission_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        cases = result.scalars().all()

        return cases, total
