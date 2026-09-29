"""
Tests for Stage 2A — PM-JAY Demo prototype.

Tests cover:
  - Demo case retrieval (org isolation)
  - Validation service (deterministic checks)
  - Execution creation
  - Execution state transitions
  - Continue / cancel operations
  - Unauthorized access
  - Invalid execution ID
  - Human-action state
  - Execution step listing

All tests use in-memory SQLite via async SQLAlchemy — no real PostgreSQL
required, no real PM-JAY portal is contacted.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.models.demo_case import DemoCase
from app.models.execution import (
    AutomationExecution,
    AutomationExecutionStep,
    ExecutionStatus,
    StepStatus,
)
from app.models.organization import Organization
from app.models.user import User
from app.services.validation import ValidationService

# ---------------------------------------------------------------------------
# SQLite in-memory test database
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


# ---------------------------------------------------------------------------
# Test data helpers
# ---------------------------------------------------------------------------


def make_org() -> Organization:
    return Organization(
        id=uuid.uuid4(),
        name="Test Hospital",
        slug=f"test-hospital-{uuid.uuid4().hex[:6]}",
        is_active=True,
    )


def make_user(org_id: uuid.UUID) -> User:
    return User(
        id=uuid.uuid4(),
        organization_id=org_id,
        email=f"test-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password=hash_password("TestPass@123"),
        full_name="Test User",
        is_active=True,
        is_admin=True,
    )


def make_demo_case(org_id: uuid.UUID, ref: str = "DEMO-TEST-001") -> DemoCase:
    return DemoCase(
        id=uuid.uuid4(),
        organization_id=org_id,
        case_ref=ref,
        demo_patient_name="SYNTHETIC TEST PATIENT",
        demo_beneficiary_id="TEST-BEN-99999",
        demo_dob=date(1990, 1, 1),
        demo_gender="Male",
        demo_hospital_name="Test Hospital",
        demo_hospital_code="TEST-HOSP-001",
        demo_procedure_name="Test Procedure",
        demo_procedure_code="TEST-PROC-001",
        demo_amount=15000.00,
        demo_documents=json.dumps(["doc1.pdf", "doc2.pdf"]),
        demo_is_synthetic=True,
        is_active=True,
    )


def make_execution(org_id: uuid.UUID, case_id: uuid.UUID) -> AutomationExecution:
    return AutomationExecution(
        id=uuid.uuid4(),
        organization_id=org_id,
        demo_case_id=case_id,
        workflow_name="PM-JAY Beneficiary / Case Processing Demo",
        initiated_by="test@example.com",
        status=ExecutionStatus.PENDING,
        current_step=0,
    )


def make_token(user_email: str, org_id: uuid.UUID) -> str:
    return create_access_token(
        subject=user_email,
        extra={"organization_id": str(org_id)},
    )


# ---------------------------------------------------------------------------
# Validation service tests (no DB, no HTTP)
# ---------------------------------------------------------------------------


class TestValidationService:
    def test_valid_case_passes_all_checks(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is True
        assert all(c["passed"] for c in checks)

    def test_empty_patient_name_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_patient_name = ""
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False
        name_check = next(c for c in checks if c["name"] == "Beneficiary name")
        assert name_check["passed"] is False

    def test_short_beneficiary_id_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_beneficiary_id = "AB"
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False
        id_check = next(c for c in checks if c["name"] == "Beneficiary ID")
        assert id_check["passed"] is False

    def test_future_dob_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_dob = date(2099, 1, 1)
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False
        dob_check = next(c for c in checks if c["name"] == "Date of birth")
        assert dob_check["passed"] is False

    def test_zero_amount_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_amount = 0
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False
        amount_check = next(c for c in checks if c["name"] == "Claim amount")
        assert amount_check["passed"] is False

    def test_non_synthetic_flag_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_is_synthetic = False
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False
        flag_check = next(c for c in checks if c["name"] == "Synthetic data flag")
        assert flag_check["passed"] is False

    def test_invalid_documents_json_fails(self):
        org_id = uuid.uuid4()
        case = make_demo_case(org_id)
        case.demo_documents = "not-json"
        svc = ValidationService()
        passed, checks = svc.validate_demo_case(case)
        assert passed is False


# ---------------------------------------------------------------------------
# FastAPI route tests — use overridden DB dependency
# ---------------------------------------------------------------------------


@pytest.fixture
async def app_with_db(engine):
    """Create app with DB dependency overridden to use test SQLite DB."""
    from app.db.session import get_db
    from app.main import create_app

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    application = create_app()
    application.dependency_overrides[get_db] = override_get_db

    mock_runner = MagicMock()
    mock_runner.start_execution = AsyncMock()
    mock_runner.continue_execution = AsyncMock()
    mock_runner.cancel_execution = AsyncMock(
        side_effect=lambda db_s, ex: setattr(ex, "status", ExecutionStatus.CANCELLED) or ex
    )
    application.state.workflow_runner = mock_runner
    application.state.browser_manager = MagicMock()
    return application


@pytest.fixture
async def seeded(engine):
    """Seed test org, user, and demo case — committed so other sessions can see it."""
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        org = make_org()
        session.add(org)
        await session.flush()
        user = make_user(org.id)
        session.add(user)
        case = make_demo_case(org.id)
        session.add(case)
        await session.commit()
    return {"org": org, "user": user, "case": case}


@pytest.fixture
async def db(engine):
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(app_with_db):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_db), base_url="http://testserver"
    ) as c:
        yield c


@pytest.fixture
def auth_headers(seeded):
    token = make_token(seeded["user"].email, seeded["org"].id)
    return {"Authorization": f"Bearer {token}"}


# --- Stage 1 health still works ---


@pytest.mark.asyncio
async def test_stage1_health_still_works(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


# --- Auth ---


@pytest.mark.asyncio
async def test_login_success(client, seeded):
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": seeded["user"].email, "password": "TestPass@123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_email"] == seeded["user"].email


@pytest.mark.asyncio
async def test_login_wrong_password(client, seeded):
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": seeded["user"].email, "password": "WrongPassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    resp = await client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@nowhere.com", "password": "anything"},
    )
    assert resp.status_code == 401


# --- Demo cases ---


@pytest.mark.asyncio
async def test_list_demo_cases_requires_auth(client):
    resp = await client.get("/api/v1/pmjay-demo/cases")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_demo_cases_returns_org_cases(client, seeded, auth_headers):
    resp = await client.get("/api/v1/pmjay-demo/cases", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["case_ref"] == "DEMO-TEST-001"
    assert data[0]["demo_is_synthetic"] is True


@pytest.mark.asyncio
async def test_org_isolation_cases(client, db):
    """Cases from org A must not appear when org B authenticates."""
    org_a = make_org()
    org_b = make_org()
    db.add(org_a)
    db.add(org_b)
    await db.flush()
    user_b = make_user(org_b.id)
    db.add(user_b)
    case_a = make_demo_case(org_a.id, ref="ORG-A-CASE")
    db.add(case_a)
    await db.commit()

    token_b = make_token(user_b.email, org_b.id)
    resp = await client.get(
        "/api/v1/pmjay-demo/cases",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 200
    refs = [c["case_ref"] for c in resp.json()]
    assert "ORG-A-CASE" not in refs


# --- Validation endpoint ---


@pytest.mark.asyncio
async def test_validate_demo_case_passes(client, seeded, auth_headers):
    case_id = str(seeded["case"].id)
    resp = await client.get(
        f"/api/v1/pmjay-demo/cases/{case_id}/validate",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is True
    assert len(data["checks"]) > 0


@pytest.mark.asyncio
async def test_validate_nonexistent_case_returns_404(client, auth_headers):
    resp = await client.get(
        f"/api/v1/pmjay-demo/cases/{uuid.uuid4()}/validate",
        headers=auth_headers,
    )
    assert resp.status_code == 404


# --- Executions ---


@pytest.mark.asyncio
async def test_create_execution_requires_auth(client, seeded):
    resp = await client.post(
        "/api/v1/pmjay-demo/executions",
        json={"demo_case_id": str(seeded["case"].id)},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_execution_success(client, seeded, auth_headers, app_with_db):
    # The background _run() closure calls AsyncSessionLocal — patch it to a no-op
    with patch("app.api.v1.pmjay_demo.AsyncSessionLocal", side_effect=Exception("skip")):
        resp = await client.post(
            "/api/v1/pmjay-demo/executions",
            json={"demo_case_id": str(seeded["case"].id)},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["status"] == "PENDING"
    assert data["workflow_name"] == "PM-JAY Beneficiary / Case Processing Demo"
    assert data["initiated_by"] == seeded["user"].email


@pytest.mark.asyncio
async def test_create_execution_wrong_case_id(client, auth_headers):
    resp = await client.post(
        "/api/v1/pmjay-demo/executions",
        json={"demo_case_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_execution_returns_correct_data(client, seeded, auth_headers, db):
    # Create directly in DB
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    db.add(execution)
    await db.commit()

    resp = await client.get(
        f"/api/v1/pmjay-demo/executions/{execution.id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(execution.id)
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_get_execution_invalid_id_returns_404(client, auth_headers):
    resp = await client.get(
        f"/api/v1/pmjay-demo/executions/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_isolation_execution(client, db, seeded):
    """Org B cannot access org A's execution."""
    org_b = make_org()
    db.add(org_b)
    await db.flush()
    user_b = make_user(org_b.id)
    db.add(user_b)
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    db.add(execution)
    await db.commit()

    token_b = make_token(user_b.email, org_b.id)
    resp = await client.get(
        f"/api/v1/pmjay-demo/executions/{execution.id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404


# --- Human-in-the-loop ---


@pytest.mark.asyncio
async def test_continue_execution_when_not_waiting_returns_400(client, seeded, auth_headers, db):
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    execution.status = ExecutionStatus.RUNNING
    db.add(execution)
    await db.commit()

    resp = await client.post(
        f"/api/v1/pmjay-demo/executions/{execution.id}/continue",
        json={"operator_note": "done"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_continue_execution_when_waiting_succeeds(
    client, seeded, auth_headers, db, app_with_db
):
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    execution.status = ExecutionStatus.WAITING_FOR_HUMAN
    execution.waiting_reason = "OTP required"
    execution.current_step = 3
    db.add(execution)
    await db.commit()

    with patch("app.api.v1.pmjay_demo.AsyncSessionLocal", side_effect=Exception("skip")):
        resp = await client.post(
            f"/api/v1/pmjay-demo/executions/{execution.id}/continue",
            json={"operator_note": "OTP entered"},
            headers=auth_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "RUNNING"


@pytest.mark.asyncio
async def test_cancel_execution(client, seeded, auth_headers, db, app_with_db):
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    execution.status = ExecutionStatus.WAITING_FOR_HUMAN
    db.add(execution)
    await db.commit()

    # Make cancel_execution actually mutate the object
    async def fake_cancel(db_session, ex):
        ex.status = ExecutionStatus.CANCELLED
        ex.completed_at = datetime.now(UTC)
        await db_session.commit()
        return ex

    app_with_db.state.workflow_runner.cancel_execution = fake_cancel

    resp = await client.post(
        f"/api/v1/pmjay-demo/executions/{execution.id}/cancel",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"


# --- Steps ---


@pytest.mark.asyncio
async def test_get_steps_empty_when_not_started(client, seeded, auth_headers, db):
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    db.add(execution)
    await db.commit()

    resp = await client.get(
        f"/api/v1/pmjay-demo/executions/{execution.id}/steps",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_steps_returns_all_steps(client, seeded, auth_headers, db):
    execution = make_execution(seeded["org"].id, seeded["case"].id)
    db.add(execution)
    await db.flush()

    # Add some steps manually
    for i in range(1, 4):
        step = AutomationExecutionStep(
            id=uuid.uuid4(),
            execution_id=execution.id,
            step_number=i,
            step_name=f"Step {i}",
            status=StepStatus.SUCCESS,
            message="OK",
        )
        db.add(step)
    await db.commit()

    resp = await client.get(
        f"/api/v1/pmjay-demo/executions/{execution.id}/steps",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    steps = resp.json()
    assert len(steps) == 3
    assert steps[0]["step_number"] == 1
    assert steps[0]["status"] == "SUCCESS"


# --- List executions ---


@pytest.mark.asyncio
async def test_list_executions_returns_own_only(client, seeded, auth_headers, db):
    for _ in range(3):
        ex = make_execution(seeded["org"].id, seeded["case"].id)
        db.add(ex)
    await db.commit()

    resp = await client.get("/api/v1/pmjay-demo/executions", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 3
