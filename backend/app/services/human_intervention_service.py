"""
HumanInterventionService — business logic for intervention lifecycle management.

Handles:
- Intervention CRUD operations
- Status transitions (PENDING → APPROVED/REJECTED)
- Escalation management
- Expiration tracking
"""

from __future__ import annotations

import uuid
import logging
from typing import Any
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.human_intervention import HumanIntervention
from app.repositories.human_intervention_repository import HumanInterventionRepository
from app.core.constants import ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class HumanInterventionService:
    """Service for human intervention lifecycle management."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.intervention_repo = HumanInterventionRepository(session)

    async def create(
        self,
        tenant_id: uuid.UUID,
        automation_id: uuid.UUID,
        title: str,
        description: str,
        reason: str,
        automation_step_id: uuid.UUID | None = None,
        is_escalated: bool = False,
        escalated_to: str | None = None,
        expires_at: datetime | None = None,
    ) -> HumanIntervention:
        """
        Create a new intervention request.

        Args:
            tenant_id: Organization ID
            automation_id: Associated automation
            title: Intervention title
            description: Detailed description
            reason: Reason for intervention
            automation_step_id: Associated step (optional)
            is_escalated: Whether escalated
            escalated_to: Escalation target
            expires_at: Expiration time

        Returns:
            Created intervention

        Raises:
            APIException: If creation fails
        """
        intervention = await self.intervention_repo.create({
            "automation_id": automation_id,
            "automation_step_id": automation_step_id,
            "title": title,
            "description": description,
            "reason": reason,
            "status": "PENDING",
            "is_escalated": is_escalated,
            "escalated_to": escalated_to,
            "expires_at": expires_at,
        })

        await self.session.commit()
        logger.info(
            f"Intervention created: {intervention.id} for automation {automation_id}"
        )
        return intervention

    async def get(
        self,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
    ) -> HumanIntervention:
        """
        Get an intervention by ID.

        Raises:
            APIException: If not found
        """
        intervention = await self.intervention_repo.read(intervention_id)
        if not intervention:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Intervention not found",
            )
        return intervention

    async def list(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        automation_id: uuid.UUID | None = None,
    ) -> tuple[list[HumanIntervention], int]:
        """
        List interventions with optional filtering.

        Args:
            tenant_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status
            automation_id: Filter by automation

        Returns:
            Tuple of (interventions, total_count)
        """
        if automation_id:
            return await self.intervention_repo.list_by_automation(
                automation_id, skip, limit
            )

        if status:
            return await self.intervention_repo.list_by_status(status, tenant_id, skip, limit)

        return await self.intervention_repo.list(
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def update(
        self,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> HumanIntervention:
        """
        Update an intervention.

        Args:
            tenant_id: Organization ID
            intervention_id: Intervention ID
            updates: Fields to update

        Returns:
            Updated intervention

        Raises:
            APIException: If not found
        """
        intervention = await self.get(tenant_id, intervention_id)

        # Allow updating certain fields
        allowed_fields = {
            "description",
            "reason",
            "is_escalated",
            "escalated_to",
            "expires_at",
        }
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if updates:
            intervention = await self.intervention_repo.update(
                intervention_id, updates
            )

        await self.session.commit()
        logger.info(f"Intervention updated: {intervention_id}")
        return intervention

    async def update_status(
        self,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
        status: str,
        decision: str | None = None,
        decision_reason: str | None = None,
        decided_by: str | None = None,
    ) -> HumanIntervention:
        """
        Update intervention status and decision.

        Args:
            tenant_id: Organization ID
            intervention_id: Intervention ID
            status: New status (APPROVED, REJECTED, ACKNOWLEDGED)
            decision: Decision value
            decision_reason: Reason for decision
            decided_by: User making decision

        Returns:
            Updated intervention

        Raises:
            APIException: If invalid transition
        """
        intervention = await self.get(tenant_id, intervention_id)

        if intervention.status != "PENDING":
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Cannot update status of {intervention.status} intervention",
            )

        if status not in ("APPROVED", "REJECTED", "ACKNOWLEDGED"):
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Invalid status: {status}",
            )

        updates = {
            "status": status,
            "decision": decision,
            "decision_reason": decision_reason,
            "decided_by": decided_by,
            "decided_at": datetime.now(timezone.utc),
        }

        intervention = await self.intervention_repo.update(
            intervention_id, updates
        )

        await self.session.commit()
        logger.info(f"Intervention status updated: {intervention_id} → {status}")
        return intervention

    async def delete(
        self,
        tenant_id: uuid.UUID,
        intervention_id: uuid.UUID,
    ) -> bool:
        """
        Delete an intervention (soft delete).

        Args:
            tenant_id: Organization ID
            intervention_id: Intervention ID

        Returns:
            True if deleted

        Raises:
            APIException: If not found
        """
        intervention = await self.get(tenant_id, intervention_id)

        # Mark as deleted
        intervention.mark_deleted(uuid.UUID(int=0))

        await self.session.commit()
        logger.info(f"Intervention deleted: {intervention_id}")
        return True

    async def list_pending(
        self,
        tenant_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[HumanIntervention], int]:
        """List all pending interventions."""
        return await self.intervention_repo.list_pending(tenant_id, skip, limit)
