"""
WorkflowService — business logic for workflow management and versioning.

Handles:
- Workflow CRUD operations
- Workflow versioning and history
- Workflow activation/publishing
- Workflow validation
"""

from __future__ import annotations

import uuid
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow
from app.models.workflow_version import WorkflowVersion
from app.repositories.workflow_repository import WorkflowRepository
from app.core.constants import WorkflowStatus, ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for workflow management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.workflow_repo = WorkflowRepository(session)

    async def create_workflow(
        self,
        organization_id: uuid.UUID,
        name: str,
        description: str | None = None,
        tags: str | None = None,
        created_by: uuid.UUID | None = None,
    ) -> Workflow:
        """
        Create a new workflow in draft status.

        Args:
            organization_id: Organization owner
            name: Workflow name
            description: Workflow description
            tags: JSON tags
            created_by: User creating the workflow

        Returns:
            Created workflow

        Raises:
            APIException: If workflow name already exists
        """
        # Check for duplicate name
        existing = await self.workflow_repo.get_by_name(name, organization_id)
        if existing:
            raise APIException(
                error_code=ErrorCode.ALREADY_EXISTS,
                message=f"Workflow with name '{name}' already exists",
            )

        # Create workflow
        workflow = await self.workflow_repo.create(
            {
                "tenant_id": organization_id,
                "name": name,
                "description": description,
                "tags": tags,
                "status": WorkflowStatus.DRAFT,
                "current_version": 1,
                "created_by": created_by,
            },
        )

        await self.session.commit()
        logger.info(f"Workflow created: {workflow.id} ({name}) for org {organization_id}")
        return workflow

    async def get_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Workflow:
        """
        Get a workflow by ID.

        Raises:
            APIException: If workflow not found or belongs to different org
        """
        workflow = await self.workflow_repo.read(workflow_id, organization_id)
        if not workflow:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Workflow not found",
            )
        return workflow

    async def list_workflows(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: WorkflowStatus | None = None,
    ) -> tuple[list[Workflow], int]:
        """
        List workflows for an organization.

        Args:
            organization_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status (optional)

        Returns:
            Tuple of (workflows, total_count)
        """
        if status:
            return await self.workflow_repo.list_by_status(
                status,
                organization_id,
                skip,
                limit,
            )

        return await self.workflow_repo.list(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
        updates: dict[str, Any],
        updated_by: uuid.UUID | None = None,
    ) -> Workflow:
        """
        Update a workflow. Only draft workflows can be updated.

        Args:
            workflow_id: Workflow ID
            organization_id: Organization ID
            updates: Fields to update
            updated_by: User updating the workflow

        Returns:
            Updated workflow

        Raises:
            APIException: If workflow not draft or not found
        """
        workflow = await self.get_workflow(workflow_id, organization_id)

        if workflow.status != WorkflowStatus.DRAFT:
            raise APIException(
                error_code=ErrorCode.OPERATION_NOT_PERMITTED,
                message="Can only edit draft workflows. Publish a new version instead.",
            )

        # Update allowed fields
        allowed_fields = {"name", "description", "tags"}
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            updates["updated_by"] = updated_by
            workflow = await self.workflow_repo.update(workflow_id, updates, organization_id)

        await self.session.commit()
        logger.info(f"Workflow updated: {workflow_id}")
        return workflow

    async def publish_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
        published_by: uuid.UUID | None = None,
    ) -> Workflow:
        """
        Publish a workflow (mark as active).

        Raises:
            APIException: If workflow not draft or not found
        """
        workflow = await self.get_workflow(workflow_id, organization_id)

        if workflow.status == WorkflowStatus.ACTIVE:
            return workflow  # Already active

        if workflow.status != WorkflowStatus.DRAFT:
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Cannot publish workflow in {workflow.status.value} status",
            )

        workflow = await self.workflow_repo.update(
            workflow_id,
            {"status": WorkflowStatus.ACTIVE, "updated_by": published_by},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Workflow published: {workflow_id}")
        return workflow

    async def archive_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
        updated_by: uuid.UUID | None = None,
    ) -> Workflow:
        """
        Archive a workflow (make inactive but preserved).

        Raises:
            APIException: If workflow not found
        """
        workflow = await self.get_workflow(workflow_id, organization_id)

        workflow = await self.workflow_repo.update(
            workflow_id,
            {"status": WorkflowStatus.ARCHIVED, "updated_by": updated_by},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Workflow archived: {workflow_id}")
        return workflow

    async def delete_workflow(
        self,
        workflow_id: uuid.UUID,
        organization_id: uuid.UUID,
        deleted_by: uuid.UUID | None = None,
    ) -> bool:
        """
        Delete a workflow (soft delete).

        Raises:
            APIException: If workflow not found
        """
        workflow = await self.get_workflow(workflow_id, organization_id)

        # Mark as deleted
        workflow.mark_deleted(deleted_by or uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Workflow deleted: {workflow_id}")
        return True

    async def list_active_workflows(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Workflow], int]:
        """List all active workflows for an organization."""
        return await self.workflow_repo.list_active(organization_id, skip, limit)

    async def list_draft_workflows(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Workflow], int]:
        """List all draft workflows for an organization."""
        return await self.workflow_repo.list_drafts(organization_id, skip, limit)
