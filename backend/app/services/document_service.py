"""
DocumentService — document upload, storage, and validation.

Handles:
- Document upload and storage
- File validation
- Duplicate detection via hashing
- Document status tracking
"""

from __future__ import annotations

import uuid
import logging
import hashlib
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.core.constants import DocumentStatus, DocumentType, ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class DocumentService:
    """Service for document management."""

    def __init__(self, session: AsyncSession, storage_path: str = "/tmp/documents"):
        """Initialize with database session and storage path."""
        self.session = session
        self.document_repo = DocumentRepository(session)
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def upload_document(
        self,
        organization_id: uuid.UUID,
        case_id: uuid.UUID | None,
        file_name: str,
        file_content: bytes,
        doc_type: DocumentType,
        mime_type: str,
        description: str | None = None,
        tags: str | None = None,
        uploaded_by: str | None = None,
    ) -> Document:
        """
        Upload a document.

        Args:
            organization_id: Organization owner
            case_id: Associated case
            file_name: Original file name
            file_content: File bytes
            doc_type: Document type
            mime_type: MIME type
            description: Document description
            tags: JSON tags
            uploaded_by: User email uploading

        Returns:
            Created document

        Raises:
            APIException: If validation fails or file too large
        """
        # Validate
        if len(file_content) > MAX_FILE_SIZE:
            raise APIException(
                error_code=ErrorCode.FILE_TOO_LARGE,
                message=f"File exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.0f}MB",
            )

        if mime_type not in ALLOWED_MIME_TYPES:
            raise APIException(
                error_code=ErrorCode.INVALID_FILE_TYPE,
                message=f"MIME type {mime_type} not allowed",
            )

        # Compute hash for duplicate detection
        hash_value = hashlib.sha256(file_content).hexdigest()

        # Check for duplicate
        existing = await self.document_repo.get_by_hash(hash_value, organization_id)
        if existing:
            logger.warning(f"Duplicate document detected: {hash_value}")
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message="This file has already been uploaded",
            )

        # Store file
        file_path = self.storage_path / f"{uuid.uuid4()}_{file_name}"
        file_path.write_bytes(file_content)

        # Create document record
        document = await self.document_repo.create(
            {
                "tenant_id": organization_id,
                "case_id": case_id,
                "document_type": doc_type,
                "file_name": file_name,
                "file_path": str(file_path),
                "file_size": len(file_content),
                "mime_type": mime_type,
                "hash_value": hash_value,
                "description": description,
                "tags": tags,
                "uploaded_by_email": uploaded_by,
                "status": DocumentStatus.PENDING,
            },
        )

        await self.session.commit()
        logger.info(f"Document uploaded: {document.id} ({file_name})")
        return document

    async def get_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Document:
        """Get document by ID."""
        document = await self.document_repo.read(document_id, organization_id)
        if not document:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Document not found",
            )
        return document

    async def download_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> tuple[bytes, str]:
        """
        Download document content.

        Returns:
            Tuple of (file_content, file_name)
        """
        document = await self.get_document(document_id, organization_id)

        try:
            content = Path(document.file_path).read_bytes()
            return content, document.file_name
        except FileNotFoundError:
            raise APIException(
                error_code=ErrorCode.FILE_NOT_FOUND,
                message="Document file not found on storage",
            )

    async def update_status(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        status: DocumentStatus,
    ) -> Document:
        """Update document status."""
        document = await self.document_repo.update(
            document_id,
            {"status": status},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Document status updated: {document_id} -> {status.value}")
        return document

    async def delete_document(
        self,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> bool:
        """Delete document (soft delete)."""
        document = await self.get_document(document_id, organization_id)

        # Delete file from storage
        try:
            Path(document.file_path).unlink()
        except FileNotFoundError:
            logger.warning(f"Document file not found for deletion: {document.file_path}")

        # Soft delete record
        document.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Document deleted: {document_id}")
        return True

    async def list_case_documents(
        self,
        case_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[Document]:
        """List all documents for a case."""
        documents, _ = await self.document_repo.list_by_case(
            case_id,
            organization_id,
            skip=0,
            limit=1000,
        )
        return documents
