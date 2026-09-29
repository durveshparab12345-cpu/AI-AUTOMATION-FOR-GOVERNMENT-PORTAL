"""
WorkflowRunner — orchestrates the PM-JAY demo workflow execution.

This service coordinates:
  BrowserSession → PMJAYAdapter → ValidationService → Database

It is the only component that mutates AutomationExecution state.
Route handlers call into this service; they never mutate state directly.

SAFETY RULES:
  - Never stores credentials, OTP values, or session tokens.
  - All sensitive portal steps pause with WAITING_FOR_HUMAN.
  - State transitions are explicit and logged.
  - If a step fails unexpectedly, the execution enters FAILED — not a retry loop.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.demo_case import DemoCase
from app.models.execution import (
    AutomationExecution,
    AutomationExecutionStep,
    ExecutionStatus,
    StepStatus,
)
from app.services.browser.browser_manager import BrowserManager
from app.services.portals.pmjay import PMJAYAdapter
from app.services.validation import ValidationService

logger = logging.getLogger(__name__)

# Canonical workflow step definitions — name and number in one place
WORKFLOW_STEPS = [
    (1, "Initialize workflow"),
    (2, "Open PM-JAY portal"),
    (3, "Authenticate operator"),
    (4, "Navigate to beneficiary section"),
    (5, "Search for beneficiary"),
    (6, "Read beneficiary information"),
    (7, "Map and validate case data"),
    (8, "Human confirmation before submission"),
    (9, "Capture portal result"),
    (10, "Complete"),
]


class WorkflowRunner:
    def __init__(self, browser_manager: BrowserManager):
        self._browser_manager = browser_manager
        self._validation = ValidationService()

    # -------------------------------------------------------------------------
    # Public API called by route handlers
    # -------------------------------------------------------------------------

    async def start_execution(
        self,
        db: AsyncSession,
        execution: AutomationExecution,
        demo_case: DemoCase,
    ) -> AutomationExecution:
        """
        Transition execution to RUNNING and begin the workflow.
        Creates all step records, then starts processing.
        """
        # Transition to RUNNING
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(execution)

        # Create all step records upfront (all PENDING)
        await self._create_step_records(db, execution)

        # Run steps sequentially
        await self._run_steps(db, execution, demo_case)
        return execution

    async def continue_execution(
        self,
        db: AsyncSession,
        execution: AutomationExecution,
        demo_case: DemoCase,
        operator_note: str | None,
    ) -> AutomationExecution:
        """
        Resume a WAITING_FOR_HUMAN execution after the operator has
        completed the required action.
        """
        if execution.status != ExecutionStatus.WAITING_FOR_HUMAN:
            return execution

        logger.info(
            "Execution %s resuming from step %d (operator note: %r)",
            execution.id,
            execution.current_step,
            operator_note,
        )
        execution.status = ExecutionStatus.RUNNING
        execution.waiting_reason = None
        await db.commit()
        await db.refresh(execution)

        # Resume from current_step
        await self._run_steps(db, execution, demo_case, resume_from=execution.current_step)
        return execution

    async def cancel_execution(
        self,
        db: AsyncSession,
        execution: AutomationExecution,
    ) -> AutomationExecution:
        """Cancel any non-terminal execution."""
        if execution.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
            return execution

        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.now(UTC)
        await db.commit()

        # Close browser if open
        await self._browser_manager.close_session(str(execution.id))
        return execution

    # -------------------------------------------------------------------------
    # Internal step execution engine
    # -------------------------------------------------------------------------

    async def _create_step_records(self, db: AsyncSession, execution: AutomationExecution) -> None:
        for step_num, step_name in WORKFLOW_STEPS:
            step = AutomationExecutionStep(
                id=uuid.uuid4(),
                execution_id=execution.id,
                step_number=step_num,
                step_name=step_name,
                status=StepStatus.PENDING,
            )
            db.add(step)
        await db.commit()

    async def _get_step(
        self, db: AsyncSession, execution_id: uuid.UUID, step_number: int
    ) -> AutomationExecutionStep | None:
        from sqlalchemy import select

        result = await db.execute(
            select(AutomationExecutionStep).where(
                AutomationExecutionStep.execution_id == execution_id,
                AutomationExecutionStep.step_number == step_number,
            )
        )
        return result.scalar_one_or_none()

    async def _update_step(
        self,
        db: AsyncSession,
        step: AutomationExecutionStep,
        status: StepStatus,
        message: str,
        metadata: dict | None = None,
    ) -> None:
        step.status = status
        step.message = message
        if metadata:
            step.step_metadata = json.dumps(metadata)
        if status == StepStatus.RUNNING and not step.started_at:
            step.started_at = datetime.now(UTC)
        if status in (StepStatus.SUCCESS, StepStatus.FAILED, StepStatus.SKIPPED):
            step.completed_at = datetime.now(UTC)
        await db.commit()

    async def _run_steps(
        self,
        db: AsyncSession,
        execution: AutomationExecution,
        demo_case: DemoCase,
        resume_from: int = 1,
    ) -> None:
        """
        Execute workflow steps sequentially starting from resume_from.
        Halts on WAITING_FOR_HUMAN, FAILED, or COMPLETED.
        """
        # Get or create browser session
        session = self._browser_manager.get_session(str(execution.id))
        if not session:
            session = await self._browser_manager.create_session(str(execution.id))

        adapter = PMJAYAdapter(session=session, demo_case=demo_case)

        for step_num, step_name in WORKFLOW_STEPS:
            if step_num < resume_from:
                continue

            step = await self._get_step(db, execution.id, step_num)
            if not step:
                continue

            execution.current_step = step_num
            await db.commit()

            await self._update_step(db, step, StepStatus.RUNNING, f"Starting: {step_name}")
            logger.info("Execution %s — running step %d: %s", execution.id, step_num, step_name)

            try:
                result = await self._execute_step(
                    step_num=step_num,
                    step_name=step_name,
                    adapter=adapter,
                    execution=execution,
                    demo_case=demo_case,
                    db=db,
                )

                if result.get("requires_human"):
                    # Pause for human intervention
                    await self._update_step(
                        db,
                        step,
                        StepStatus.WAITING_FOR_HUMAN,
                        result.get("message", "Waiting for human action"),
                        result.get("data"),
                    )
                    execution.status = ExecutionStatus.WAITING_FOR_HUMAN
                    execution.waiting_reason = result.get("human_reason", "Human action required")
                    if result.get("screenshot_path"):
                        execution.last_screenshot_path = result["screenshot_path"]
                    await db.commit()
                    logger.info(
                        "Execution %s paused at step %d — waiting for human: %s",
                        execution.id,
                        step_num,
                        execution.waiting_reason,
                    )
                    return  # Stop — wait for continue_execution() call

                elif not result.get("success"):
                    await self._update_step(
                        db,
                        step,
                        StepStatus.FAILED,
                        result.get("message", "Step failed"),
                        result.get("data"),
                    )
                    execution.status = ExecutionStatus.FAILED
                    execution.error_message = result.get("message", "Step failed")
                    execution.completed_at = datetime.now(UTC)
                    await db.commit()
                    await self._browser_manager.close_session(str(execution.id))
                    return

                else:
                    await self._update_step(
                        db,
                        step,
                        StepStatus.SUCCESS,
                        result.get("message", "Completed"),
                        result.get("data"),
                    )
                    if result.get("screenshot_path"):
                        execution.last_screenshot_path = result["screenshot_path"]
                    await db.commit()

            except Exception as exc:
                logger.exception("Unexpected error at step %d", step_num)
                await self._update_step(db, step, StepStatus.FAILED, str(exc))
                execution.status = ExecutionStatus.FAILED
                execution.error_message = str(exc)
                execution.completed_at = datetime.now(UTC)
                await db.commit()
                await self._browser_manager.close_session(str(execution.id))
                return

        # All steps completed
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.now(UTC)
        await db.commit()
        await self._browser_manager.close_session(str(execution.id))
        logger.info("Execution %s COMPLETED", execution.id)

    async def _execute_step(
        self,
        step_num: int,
        step_name: str,
        adapter: PMJAYAdapter,
        execution: AutomationExecution,
        demo_case: DemoCase,
        db: AsyncSession,
    ) -> dict:
        """Map step numbers to adapter calls. Returns a result dict."""

        if step_num == 1:
            # Initialize — run validation
            execution.status = ExecutionStatus.VALIDATING
            await db.commit()
            passed, checks = self._validation.validate_demo_case(demo_case)
            if not passed:
                failed_checks = [c["name"] for c in checks if not c["passed"]]
                return {
                    "success": False,
                    "message": f"Validation failed: {', '.join(failed_checks)}",
                    "data": {"validation_checks": checks},
                }
            execution.status = ExecutionStatus.RUNNING
            await db.commit()
            return {
                "success": True,
                "message": "Workflow initialized — all validation checks passed",
                "data": {"validation_checks": checks},
            }

        elif step_num == 2:
            result = await adapter.connect()
            return _adapter_result_to_dict(result)

        elif step_num == 3:
            result = await adapter.authenticate(credentials_ref="operator_credentials")
            return _adapter_result_to_dict(result)

        elif step_num == 4:
            result = await adapter.navigate_to_section("Beneficiary Search")
            return _adapter_result_to_dict(result)

        elif step_num == 5:
            result = await adapter.search(demo_case.demo_beneficiary_id)
            return _adapter_result_to_dict(result)

        elif step_num == 6:
            result = await adapter.read_page()
            return _adapter_result_to_dict(result)

        elif step_num == 7:
            # Data mapping + portal validation
            mapping = {
                "demo_patient_name": demo_case.demo_patient_name,
                "demo_beneficiary_id": demo_case.demo_beneficiary_id,
                "demo_procedure_code": demo_case.demo_procedure_code,
                "demo_hospital_code": demo_case.demo_hospital_code,
            }
            return {
                "success": True,
                "message": "Case data mapped to portal fields",
                "data": {"field_mapping": mapping},
            }

        elif step_num == 8:
            # ALWAYS pause before any consequential action
            result = await adapter.request_human_action(
                "Human confirmation required before any consequential portal submission. "
                "Please review the mapped data, confirm it is correct, and click Continue "
                "to proceed — or click Stop to cancel the workflow."
            )
            return _adapter_result_to_dict(result)

        elif step_num == 9:
            # Capture whatever result the portal shows — no fabrication
            result = await adapter.read_page()
            d = _adapter_result_to_dict(result)
            # Store portal result — only real data
            execution.portal_result = json.dumps(d.get("data", {}))
            await db.commit()
            return d

        elif step_num == 10:
            return {"success": True, "message": "Workflow complete"}

        return {"success": True, "message": step_name}


def _adapter_result_to_dict(result) -> dict:
    return {
        "success": result.success,
        "message": result.message,
        "requires_human": result.requires_human,
        "human_reason": result.human_reason,
        "data": result.data,
        "screenshot_path": result.screenshot_path,
    }
