"""
Document model — track uploaded case documents.

Documents can be evidence, receipts, medical records, etc. associated with cases.
Supports versioning, validation, and status tracking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Text, Enum as SQLEnum, ForeignKey, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DocumentType, DocumentStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.case import Case


class Document(BaseModel):
    """
    Document associated with a case.
    
    Tracks files submitted for a case with versioning, validation,
    and status tracking.
    """

    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_case_id", "case_id"),
        Index("ix_documents_status", "status"),
        Index("ix_documents_document_type", "document_type"),
    )

    # References
    case_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Classification
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType),
        nullable=False,
        default=DocumentType.OTHER,
    )

    # File storage
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_size: Mapped[int] = mapped_column(default=0)  # Bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Validation
    hash_value: Mapped[str | None] = mapped_column(String(255), nullable=True)  # SHA256
    is_verified: Mapped[bool] = mapped_column(default=False)

    # Status
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        nullable=False,
        default=DocumentStatus.PENDING,
        index=True,
    )

    # Metadata
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Upload tracking
    uploaded_by_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    # Relationships
    case: Mapped[Case | None] = relationship(
        "Case",
        back_populates="documents",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Document(id={self.id}, file_name={self.file_name}, status={self.status.value})>"

    @property
    def is_valid(self) -> bool:
        """Check if document is valid."""
        return self.status in (DocumentStatus.ACCEPTED, DocumentStatus.SUBMITTED)

    @property
    def requires_review(self) -> bool:
        """Check if document requires review."""
        return self.status == DocumentStatus.REVIEW_REQUIRED
