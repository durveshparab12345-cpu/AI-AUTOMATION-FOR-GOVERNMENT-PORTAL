"""
PortalService — business logic for portal management and versioning.

Handles:
- Portal CRUD operations
- Portal version management
- Portal discovery and listing
- Portal activation/deactivation
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portal import Portal
from app.models.portal_version import PortalVersion
from app.repositories.portal_repository import PortalRepository
from app.core.constants import PortalStatus, ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class PortalService:
    """Service for portal management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.portal_repo = PortalRepository(session)

    async def create_portal(
        self,
        organization_id: uuid.UUID,
        name: str,
        base_url: str,
        portal_type: str,
        auth_type: str = "BASIC",
        description: str | None = None,
        metadata: str | None = None,
        created_by: uuid.UUID | None = None,
    ) -> Portal:
        """
        Create a new portal.

        Args:
            organization_id: Organization owner
            name: Portal name
            base_url: Portal URL
            portal_type: Portal type (PMJAY, TPA, etc)
            auth_type: Authentication method
            description: Portal description
            metadata: JSON metadata
            created_by: User creating the portal

        Returns:
            Created portal

        Raises:
            APIException: If portal name already exists
        """
        # Check for duplicate name
        existing = await self.portal_repo.get_by_name(name, organization_id)
        if existing:
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message=f"Portal with name '{name}' already exists",
            )

        # Create portal
        portal = await self.portal_repo.create(
            {
                "tenant_id": organization_id,
                "name": name,
                "base_url": base_url,
                "type": portal_type,
                "auth_type": auth_type,
                "description": description,
                "metadata": metadata,
                "status": PortalStatus.DRAFT,
                "created_by": created_by,
            },
        )

        await self.session.commit()
        logger.info(f"Portal created: {portal.id} ({name}) for org {organization_id}")
        return portal

    async def get_portal(
        self,
        portal_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Portal:
        """
        Get a portal by ID.

        Raises:
            APIException: If portal not found or belongs to different org
        """
        portal = await self.portal_repo.read(portal_id, organization_id)
        if not portal:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Portal not found",
            )
        return portal

    async def list_portals(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: PortalStatus | None = None,
    ) -> tuple[list[Portal], int]:
        """
        List portals for an organization.

        Args:
            organization_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status (optional)

        Returns:
            Tuple of (portals, total_count)
        """
        if status:
            return await self.portal_repo.list_by_status(
                status,
                organization_id,
                skip,
                limit,
            )

        return await self.portal_repo.list(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update_portal(
        self,
        portal_id: uuid.UUID,
        organization_id: uuid.UUID,
        updates: dict[str, Any],
        updated_by: uuid.UUID | None = None,
    ) -> Portal:
        """
        Update a portal.

        Args:
            portal_id: Portal ID
            organization_id: Organization ID
            updates: Fields to update
            updated_by: User updating the portal

        Returns:
            Updated portal

        Raises:
            APIException: If portal not found
        """
        portal = await self.get_portal(portal_id, organization_id)

        # Prevent status changes directly (use activate/deactivate)
        if "status" in updates and updates["status"] != portal.status:
            raise APIException(
                error_code=ErrorCode.OPERATION_NOT_PERMITTED,
                message="Use activate/deactivate endpoints to change portal status",
            )

        # Update allowed fields
        allowed_fields = {"name", "description", "metadata", "base_url", "auth_type"}
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            updates["updated_by"] = updated_by
            portal = await self.portal_repo.update(portal_id, updates, organization_id)

        await self.session.commit()
        logger.info(f"Portal updated: {portal_id}")
        return portal

    async def activate_portal(
        self,
        portal_id: uuid.UUID,
        organization_id: uuid.UUID,
        updated_by: uuid.UUID | None = None,
    ) -> Portal:
        """
        Activate a portal.

        Raises:
            APIException: If portal not configured or not found
        """
        portal = await self.get_portal(portal_id, organization_id)

        if portal.status == PortalStatus.ACTIVE:
            return portal  # Already active

        if portal.status not in (PortalStatus.CONFIGURED, PortalStatus.DRAFT):
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Cannot activate portal in {portal.status.value} status",
            )

        portal = await self.portal_repo.update(
            portal_id,
            {"status": PortalStatus.ACTIVE, "updated_by": updated_by},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Portal activated: {portal_id}")
        return portal

    async def deactivate_portal(
        self,
        portal_id: uuid.UUID,
        organization_id: uuid.UUID,
        updated_by: uuid.UUID | None = None,
    ) -> Portal:
        """
        Deactivate a portal.

        Raises:
            APIException: If portal not found
        """
        portal = await self.get_portal(portal_id, organization_id)

        if portal.status == PortalStatus.INACTIVE:
            return portal  # Already inactive

        portal = await self.portal_repo.update(
            portal_id,
            {"status": PortalStatus.INACTIVE, "updated_by": updated_by},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Portal deactivated: {portal_id}")
        return portal

    async def delete_portal(
        self,
        portal_id: uuid.UUID,
        organization_id: uuid.UUID,
        deleted_by: uuid.UUID | None = None,
    ) -> bool:
        """
        Delete a portal (soft delete).

        Raises:
            APIException: If portal not found
        """
        portal = await self.get_portal(portal_id, organization_id)

        # Mark as deleted
        portal.mark_deleted(deleted_by or uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Portal deleted: {portal_id}")
        return True

    async def list_active_portals(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Portal], int]:
        """List all active portals for an organization."""
        return await self.portal_repo.list_active(organization_id, skip, limit)
