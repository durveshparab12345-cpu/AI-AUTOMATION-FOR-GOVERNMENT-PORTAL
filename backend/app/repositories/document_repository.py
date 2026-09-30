"""
DocumentRepository — data access for Document model.

Handles document queries including type and status filtering.
"""

from __future__ import annotations

import uuid

from sqlalchemy import and_, select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.core.constants import DocumentType, DocumentStatus
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for Document model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def list_by_case(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Document], int]:
        """List all documents for a case."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.case_id == case_id,
                    Document.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.case_id == case_id,
                    Document.tenant_id == organization_id,
                )
            )
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        documents = result.scalars().all()

        return documents, total

    async def list_by_type(
        self,
        doc_type: DocumentType,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Document], int]:
        """List all documents of a specific type."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.document_type == doc_type,
                    Document.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.document_type == doc_type,
                    Document.tenant_id == organization_id,
                )
            )
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        documents = result.scalars().all()

        return documents, total

    async def list_by_status(
        self,
        status: DocumentStatus,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Document], int]:
        """List all documents with a specific status."""
        # Count
        count_result = await self.session.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.status == status,
                    Document.tenant_id == organization_id,
                )
            )
        )
        total = count_result.scalar() or 0

        # List
        stmt = (
            select(Document)
            .where(
                and_(
                    Document.status == status,
                    Document.tenant_id == organization_id,
                )
            )
            .order_by(desc(Document.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        documents = result.scalars().all()

        return documents, total

    async def get_by_hash(
        self,
        hash_value: str,
        organization_id: uuid.UUID,
    ) -> Document | None:
        """Get document by hash (for duplicate detection)."""
        stmt = select(Document).where(
            and_(
                Document.hash_value == hash_value,
                Document.tenant_id == organization_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
