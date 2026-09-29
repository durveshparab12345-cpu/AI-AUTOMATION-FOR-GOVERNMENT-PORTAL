"""
PM-JAY Demo API routes.

All endpoints require authentication and enforce organization isolation.
No route handler contains business logic — all logic lives in services.

Endpoints:
  GET  /api/v1/pmjay-demo/cases
  POST /api/v1/pmjay-demo/executions
  GET  /api/v1/pmjay-demo/executions
  GET  /api/v1/pmjay-demo/executions/{execution_id}
  GET  /api/v1/pmjay-demo/executions/{execution_id}/steps
  POST /api/v1/pmjay-demo/executions/{execution_id}/continue
  POST /api/v1/pmjay-demo/executions/{execution_id}/cancel
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_org_id, get_current_user_email
from app.db.session import AsyncSessionLocal, get_db
from app.models.execution import AutomationExecution, ExecutionStatus
from app.repositories.demo_case_repository import DemoCaseRepository
from app.repositories.execution_repository import ExecutionRepository
from app.schemas.demo_case import DemoCaseRead
from app.schemas.execution import (
    ContinueRequest,
    ExecutionCreate,
    ExecutionRead,
    ExecutionStepRead,
    ValidationResult,
)
from app.services.validation import ValidationService
from app.services.workflow_runner import WorkflowRunner

router = APIRouter(prefix="/pmjay-demo", tags=["PM-JAY Demo"])


def _get_workflow_runner(request: Request) -> WorkflowRunner:
    """Retrieve the WorkflowRunner from application state."""
    return request.app.state.workflow_runner


# ---------------------------------------------------------------------------
# Demo cases
# ---------------------------------------------------------------------------


@router.get("/cases", response_model=list[DemoCaseRead])
async def list_demo_cases(
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> list[DemoCaseRead]:
    """List all active demo cases for the authenticated organization."""
    repo = DemoCaseRepository(db)
    cases = await repo.list_active(org_id)
    return [DemoCaseRead.model_validate(c) for c in cases]


@router.get("/cases/{case_id}/validate", response_model=ValidationResult)
async def validate_demo_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> ValidationResult:
    """Run validation checks on a demo case without starting a workflow."""
    repo = DemoCaseRepository(db)
    case = await repo.get_by_id(case_id, org_id)
    if not case:
        raise HTTPException(status_code=404, detail="Demo case not found")

    svc = ValidationService()
    passed, checks = svc.validate_demo_case(case)
    return ValidationResult(passed=passed, checks=checks)


# ---------------------------------------------------------------------------
# Executions
# ---------------------------------------------------------------------------


@router.post("/executions", response_model=ExecutionRead, status_code=status.HTTP_201_CREATED)
async def create_execution(
    payload: ExecutionCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
    user_email: str = Depends(get_current_user_email),
) -> ExecutionRead:
    """
    Create a new workflow execution and start it in the background.
    The execution begins immediately — the browser will open on the server.
    """
    # Verify the demo case belongs to this org
    case_repo = DemoCaseRepository(db)
    demo_case = await case_repo.get_by_id(payload.demo_case_id, org_id)
    if not demo_case:
        raise HTTPException(status_code=404, detail="Demo case not found")

    # Create the execution record
    execution = AutomationExecution(
        id=uuid.uuid4(),
        organization_id=org_id,
        demo_case_id=demo_case.id,
        workflow_name=payload.workflow_name,
        initiated_by=user_email,
        status=ExecutionStatus.PENDING,
        current_step=0,
    )
    exec_repo = ExecutionRepository(db)
    execution = await exec_repo.create(execution)

    # Start the workflow in the background so we can return the ID immediately
    runner = _get_workflow_runner(request)

    async def _run():
        try:
            async with AsyncSessionLocal() as bg_db:
                bg_case_repo = DemoCaseRepository(bg_db)
                bg_demo_case = await bg_case_repo.get_by_id(demo_case.id, org_id)
                from sqlalchemy import select

                from app.models.execution import AutomationExecution as AE

                result = await bg_db.execute(select(AE).where(AE.id == execution.id))
                bg_execution = result.scalar_one()
                await runner.start_execution(bg_db, bg_execution, bg_demo_case)
        except Exception as exc:
            import logging

            logging.getLogger(__name__).error("Background execution error: %s", exc)

    background_tasks.add_task(_run)

    # Return the execution (reload with relationships)
    created = await exec_repo.get_by_id(execution.id, org_id)
    return ExecutionRead.model_validate(created)


@router.get("/executions", response_model=list[ExecutionRead])
async def list_executions(
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> list[ExecutionRead]:
    """List recent executions for the authenticated organization."""
    repo = ExecutionRepository(db)
    executions = await repo.list_by_org(org_id)
    return [ExecutionRead.model_validate(e) for e in executions]


@router.get("/executions/{execution_id}", response_model=ExecutionRead)
async def get_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> ExecutionRead:
    """Get a single execution by ID (org-scoped)."""
    repo = ExecutionRepository(db)
    execution = await repo.get_by_id(execution_id, org_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionRead.model_validate(execution)


@router.get("/executions/{execution_id}/steps", response_model=list[ExecutionStepRead])
async def get_execution_steps(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> list[ExecutionStepRead]:
    """Get all steps for an execution."""
    repo = ExecutionRepository(db)
    steps = await repo.get_steps(execution_id, org_id)
    if not steps:
        # Check if execution exists at all
        execution = await repo.get_by_id(execution_id, org_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
    return [ExecutionStepRead.model_validate(s) for s in steps]


@router.post("/executions/{execution_id}/continue", response_model=ExecutionRead)
async def continue_execution(
    execution_id: uuid.UUID,
    payload: ContinueRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> ExecutionRead:
    """
    Resume a WAITING_FOR_HUMAN execution after the operator has
    completed the required manual action.
    """
    repo = ExecutionRepository(db)
    execution = await repo.get_by_id(execution_id, org_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status != ExecutionStatus.WAITING_FOR_HUMAN:
        raise HTTPException(
            status_code=400,
            detail=f"Execution is not waiting for human action (status: {execution.status})",
        )

    case_repo = DemoCaseRepository(db)
    demo_case = await case_repo.get_by_id(execution.demo_case_id, org_id)
    if not demo_case:
        raise HTTPException(status_code=404, detail="Demo case not found")

    runner = _get_workflow_runner(request)

    async def _resume():
        try:
            async with AsyncSessionLocal() as bg_db:
                from sqlalchemy import select

                from app.models.demo_case import DemoCase as DC
                from app.models.execution import AutomationExecution as AE

                result = await bg_db.execute(select(AE).where(AE.id == execution_id))
                bg_execution = result.scalar_one()
                result2 = await bg_db.execute(select(DC).where(DC.id == demo_case.id))
                bg_case = result2.scalar_one()
                await runner.continue_execution(bg_db, bg_execution, bg_case, payload.operator_note)
        except Exception as exc:
            import logging

            logging.getLogger(__name__).error("Background resume error: %s", exc)

    background_tasks.add_task(_resume)

    # Mark as running immediately so the UI reflects the change
    execution.status = ExecutionStatus.RUNNING
    execution.waiting_reason = None
    await db.commit()
    await db.refresh(execution)
    return ExecutionRead.model_validate(execution)


@router.post("/executions/{execution_id}/cancel", response_model=ExecutionRead)
async def cancel_execution(
    execution_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    org_id: uuid.UUID = Depends(get_current_org_id),
) -> ExecutionRead:
    """Cancel a running or waiting execution."""
    repo = ExecutionRepository(db)
    execution = await repo.get_by_id(execution_id, org_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    runner = _get_workflow_runner(request)
    execution = await runner.cancel_execution(db, execution)
    await db.refresh(execution)
    return ExecutionRead.model_validate(execution)
