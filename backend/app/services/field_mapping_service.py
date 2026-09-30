"""
FieldMappingService — business logic for field mapping and translation.

Handles:
- Field mapping CRUD operations
- Workflow-specific mappings
- Validation rule management
- Bidirectional transformation logic
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field_mapping import FieldMapping
from app.repositories.field_mapping_repository import FieldMappingRepository
from app.core.constants import ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class FieldMappingService:
    """Service for field mapping and translation."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.mapping_repo = FieldMappingRepository(session)

    async def create(
        self,
        tenant_id: uuid.UUID,
        workflow_id: uuid.UUID,
        portal_field: str,
        system_field: str,
        mapping_type: str = "DIRECT",
        direction: str = "BIDIRECTIONAL",
        transformation_logic: str | None = None,
        validation_rules: str | None = None,
        is_required: bool = False,
        description: str | None = None,
    ) -> FieldMapping:
        """
        Create a new field mapping.

        Args:
            tenant_id: Organization ID
            workflow_id: Associated workflow
            portal_field: Portal field name
            system_field: System field name
            mapping_type: Type (DIRECT, TRANSFORM, COMPUTED, LOOKUP)
            direction: Direction (INPUT, OUTPUT, BIDIRECTIONAL)
            transformation_logic: Transformation logic (JSON/code)
            validation_rules: Validation rules (JSON)
            is_required: Whether field is required
            description: Mapping description

        Returns:
            Created field mapping

        Raises:
            APIException: If creation fails or duplicate
        """
        # Check for duplicate mapping
        existing = await self.mapping_repo.get_by_fields(
            workflow_id, portal_field, system_field
        )
        if existing:
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message=f"Mapping already exists for {portal_field} ↔ {system_field}",
            )

        mapping = await self.mapping_repo.create({
            "workflow_id": workflow_id,
            "portal_field": portal_field,
            "system_field": system_field,
            "mapping_type": mapping_type,
            "direction": direction,
            "transformation_logic": transformation_logic,
            "validation_rules": validation_rules,
            "is_required": is_required,
            "description": description,
        })

        await self.session.commit()
        logger.info(
            f"Field mapping created: {mapping.id} ({portal_field} ↔ {system_field})"
        )
        return mapping

    async def get(
        self,
        tenant_id: uuid.UUID,
        mapping_id: uuid.UUID,
    ) -> FieldMapping:
        """
        Get a field mapping by ID.

        Raises:
            APIException: If not found
        """
        mapping = await self.mapping_repo.read(mapping_id)
        if not mapping:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Field mapping not found",
            )
        return mapping

    async def list(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        workflow_id: uuid.UUID | None = None,
        mapping_type: str | None = None,
        required_only: bool = False,
    ) -> tuple[list[FieldMapping], int]:
        """
        List field mappings with optional filtering.

        Args:
            tenant_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            workflow_id: Filter by workflow
            mapping_type: Filter by type
            required_only: Only required fields

        Returns:
            Tuple of (mappings, total_count)
        """
        if workflow_id:
            return await self.mapping_repo.list_by_workflow(
                workflow_id, skip, limit
            )

        if mapping_type:
            return await self.mapping_repo.list_by_type(
                mapping_type, skip, limit
            )

        if required_only:
            return await self.mapping_repo.list_required(skip, limit)

        return await self.mapping_repo.list(
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update(
        self,
        tenant_id: uuid.UUID,
        mapping_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> FieldMapping:
        """
        Update a field mapping.

        Args:
            tenant_id: Organization ID
            mapping_id: Mapping ID
            updates: Fields to update

        Returns:
            Updated field mapping

        Raises:
            APIException: If not found
        """
        mapping = await self.get(tenant_id, mapping_id)

        # Allow updating certain fields
        allowed_fields = {
            "mapping_type",
            "direction",
            "transformation_logic",
            "validation_rules",
            "is_required",
            "description",
        }
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            mapping = await self.mapping_repo.update(mapping_id, updates)

        await self.session.commit()
        logger.info(f"Field mapping updated: {mapping_id}")
        return mapping

    async def validate_mapping(
        self,
        tenant_id: uuid.UUID,
        mapping_id: uuid.UUID,
        value: Any,
    ) -> bool:
        """
        Validate a value against mapping rules.

        Args:
            tenant_id: Organization ID
            mapping_id: Mapping ID
            value: Value to validate

        Returns:
            True if valid

        Raises:
            APIException: If validation fails
        """
        mapping = await self.get(tenant_id, mapping_id)

        # TODO: Implement validation logic based on validation_rules
        # For now, just check if required
        if mapping.is_required and not value:
            raise APIException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message=f"Field {mapping.portal_field} is required",
            )

        return True

    async def transform_value(
        self,
        tenant_id: uuid.UUID,
        mapping_id: uuid.UUID,
        value: Any,
        direction: str = "output",
    ) -> Any:
        """
        Transform a value using mapping transformation logic.

        Args:
            tenant_id: Organization ID
            mapping_id: Mapping ID
            value: Value to transform
            direction: 'input' or 'output'

        Returns:
            Transformed value

        Raises:
            APIException: If mapping not found
        """
        mapping = await self.get(tenant_id, mapping_id)

        # TODO: Implement transformation logic based on transformation_logic
        # For now, return value as-is
        return value

    async def delete(
        self,
        tenant_id: uuid.UUID,
        mapping_id: uuid.UUID,
    ) -> bool:
        """
        Delete a field mapping (soft delete).

        Args:
            tenant_id: Organization ID
            mapping_id: Mapping ID

        Returns:
            True if deleted

        Raises:
            APIException: If not found
        """
        mapping = await self.get(tenant_id, mapping_id)

        # Mark as deleted
        mapping.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Field mapping deleted: {mapping_id}")
        return True

    async def list_by_workflow(
        self,
        tenant_id: uuid.UUID,
        workflow_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FieldMapping], int]:
        """List all mappings for a workflow."""
        return await self.mapping_repo.list_by_workflow(
            workflow_id, skip, limit
        )

    async def list_required_fields(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[FieldMapping], int]:
        """List all required field mappings."""
        return await self.mapping_repo.list_required(skip, limit)
