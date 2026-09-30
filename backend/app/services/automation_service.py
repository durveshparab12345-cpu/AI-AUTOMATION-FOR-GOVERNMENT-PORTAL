"""
AutomationService — business logic for automation execution orchestration.

Handles:
- Automation instance creation and lifecycle
- Automation step tracking
- Automation pause/resume for human intervention
- Automation completion and error handling
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.automation import Automation
from app.models.automation_step import AutomationStep
from app.repositories.automation_repository import AutomationRepository
from app.repositories.automation_step_repository import AutomationStepRepository
from app.core.constants import ExecutionStatus, StepStatus, ErrorCode
from app.exceptions import APIException

logger = logging.getLogger(__name__)


class AutomationService:
    """Service for automation execution orchestration."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.automation_repo = AutomationRepository(session)
        self.step_repo = AutomationStepRepository(session)

    async def create_automation(
        self,
        organization_id: uuid.UUID,
        workflow_id: uuid.UUID,
        portal_id: uuid.UUID,
        case_id: uuid.UUID | None = None,
        metadata: str | None = None,
        created_by: uuid.UUID | None = None,
    ) -> Automation:
        """
        Create a new automation instance.

        Args:
            organization_id: Organization owner
            workflow_id: Workflow to execute
            portal_id: Portal to interact with
            case_id: Associated case (optional)
            metadata: JSON metadata
            created_by: User creating the automation

        Returns:
            Created automation
        """
        automation = await self.automation_repo.create(
            {
                "tenant_id": organization_id,
                "workflow_id": workflow_id,
                "portal_id": portal_id,
                "case_id": case_id,
                "status": ExecutionStatus.PENDING,
                "current_step": 0,
                "metadata": metadata,
                "created_by": created_by,
            },
        )

        await self.session.commit()
        logger.info(
            f"Automation created: {automation.id} "
            f"(workflow={workflow_id}, case={case_id}) for org {organization_id}"
        )
        return automation

    async def get_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Automation:
        """
        Get an automation by ID.

        Raises:
            APIException: If automation not found or belongs to different org
        """
        automation = await self.automation_repo.read(automation_id, organization_id)
        if not automation:
            raise APIException(
                error_code=ErrorCode.NOT_FOUND,
                message="Automation not found",
            )
        return automation

    async def list_automations(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: ExecutionStatus | None = None,
    ) -> tuple[list[Automation], int]:
        """
        List automations for an organization.

        Args:
            organization_id: Organization ID
            skip: Pagination offset
            limit: Pagination limit
            status: Filter by status (optional)

        Returns:
            Tuple of (automations, total_count)
        """
        if status:
            return await self.automation_repo.list_by_status(
                status,
                organization_id,
                skip,
                limit,
            )

        return await self.automation_repo.list(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            order_by="created_at",
            order_desc=True,
        )

    async def start_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Automation:
        """
        Start an automation (transition from PENDING to RUNNING).

        Raises:
            APIException: If automation not in correct state
        """
        automation = await self.get_automation(automation_id, organization_id)

        if automation.status != ExecutionStatus.PENDING:
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message=f"Cannot start automation in {automation.status.value} state",
            )

        automation = await self.automation_repo.update(
            automation_id,
            {
                "status": ExecutionStatus.RUNNING,
                "started_at": datetime.now(timezone.utc),
            },
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Automation started: {automation_id}")
        return automation

    async def pause_for_human_intervention(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
        reason: str,
    ) -> Automation:
        """
        Pause automation waiting for human decision.

        Args:
            automation_id: Automation ID
            organization_id: Organization ID
            reason: Reason for human intervention

        Returns:
            Updated automation

        Raises:
            APIException: If automation not found
        """
        automation = await self.get_automation(automation_id, organization_id)

        automation = await self.automation_repo.update(
            automation_id,
            {
                "status": ExecutionStatus.WAITING_FOR_HUMAN,
                "waiting_reason": reason,
            },
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Automation paused for human intervention: {automation_id}")
        return automation

    async def resume_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Automation:
        """
        Resume a paused automation.

        Raises:
            APIException: If automation not waiting for human
        """
        automation = await self.get_automation(automation_id, organization_id)

        if automation.status != ExecutionStatus.WAITING_FOR_HUMAN:
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message="Automation is not waiting for human intervention",
            )

        automation = await self.automation_repo.update(
            automation_id,
            {"status": ExecutionStatus.RUNNING},
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Automation resumed: {automation_id}")
        return automation

    async def complete_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
        result_data: str | None = None,
    ) -> Automation:
        """
        Complete an automation successfully.

        Returns:
            Updated automation

        Raises:
            APIException: If automation not found
        """
        automation = await self.get_automation(automation_id, organization_id)

        automation = await self.automation_repo.update(
            automation_id,
            {
                "status": ExecutionStatus.COMPLETED,
                "completed_at": datetime.now(timezone.utc),
                "result_data": result_data,
            },
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Automation completed: {automation_id}")
        return automation

    async def fail_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
        error_message: str,
    ) -> Automation:
        """
        Mark an automation as failed.

        Returns:
            Updated automation

        Raises:
            APIException: If automation not found
        """
        automation = await self.get_automation(automation_id, organization_id)

        automation = await self.automation_repo.update(
            automation_id,
            {
                "status": ExecutionStatus.FAILED,
                "completed_at": datetime.now(timezone.utc),
                "error_message": error_message,
            },
            organization_id,
        )

        await self.session.commit()
        logger.error(f"Automation failed: {automation_id} - {error_message}")
        return automation

    async def cancel_automation(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Automation:
        """
        Cancel an automation.

        Returns:
            Updated automation

        Raises:
            APIException: If automation not found
        """
        automation = await self.get_automation(automation_id, organization_id)

        if automation.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED):
            raise APIException(
                error_code=ErrorCode.INVALID_STATE_TRANSITION,
                message="Cannot cancel a completed or already-cancelled automation",
            )

        automation = await self.automation_repo.update(
            automation_id,
            {
                "status": ExecutionStatus.CANCELLED,
                "completed_at": datetime.now(timezone.utc),
            },
            organization_id,
        )

        await self.session.commit()
        logger.info(f"Automation cancelled: {automation_id}")
        return automation

    async def create_step(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
        step_number: int,
        step_name: str,
        node_id: uuid.UUID | None = None,
    ) -> AutomationStep:
        """
        Create a step within an automation.

        Returns:
            Created step
        """
        step = await self.step_repo.create(
            {
                "tenant_id": organization_id,
                "automation_id": automation_id,
                "workflow_node_id": node_id,
                "step_number": step_number,
                "step_name": step_name,
                "status": StepStatus.PENDING,
            },
        )

        await self.session.commit()
        logger.info(f"Automation step created: {step.id} (#{step_number} {step_name})")
        return step

    async def update_step_status(
        self,
        step_id: uuid.UUID,
        organization_id: uuid.UUID,
        status: StepStatus,
        message: str | None = None,
        result_data: str | None = None,
    ) -> AutomationStep:
        """
        Update step status and results.

        Returns:
            Updated step
        """
        updates: dict[str, Any] = {"status": status}
        if message:
            updates["message"] = message
        if result_data:
            updates["result_data"] = result_data

        if status in (StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED):
            updates["completed_at"] = datetime.now(timezone.utc)

        step = await self.step_repo.update(step_id, updates, organization_id)

        await self.session.commit()
        logger.info(f"Step status updated: {step_id} -> {status.value}")
        return step

    async def list_automation_steps(
        self,
        automation_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> list[AutomationStep]:
        """List all steps for an automation."""
        steps, _ = await self.step_repo.list_by_automation(
            automation_id,
            organization_id,
            skip=0,
            limit=1000,
        )
        return steps

    async def list_waiting_automations(
        self,
        organization_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Automation], int]:
        """List automations waiting for human intervention."""
        return await self.automation_repo.list_waiting_for_human(
            organization_id,
            skip,
            limit,
        )
