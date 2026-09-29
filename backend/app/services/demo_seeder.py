"""
Demo data seeder.

Seeds the database with synthetic demo cases and a demo organization/user
on first startup when DEMO_MODE=true.

SYNTHETIC DATA ONLY — all names, IDs, and numbers are obviously fictitious.
NO real patient, beneficiary, or employee data is used here.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.demo_case import DemoCase
from app.models.organization import Organization
from app.models.user import User

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic demo organization
# ---------------------------------------------------------------------------
DEMO_ORG_SLUG = "demo-hospital"
DEMO_ORG_NAME = "Demo General Hospital (SYNTHETIC)"

# ---------------------------------------------------------------------------
# Demo user — password is displayed in logs on first seed so the operator
# can log in during the presentation.  Change this before any real deployment.
# ---------------------------------------------------------------------------
DEMO_USER_EMAIL = "demo@ai-portal-demo.local"
DEMO_USER_PASSWORD = "DemoPassword@2026"  # noqa: S105 — demo only, not production
DEMO_USER_NAME = "Demo Operator"

# ---------------------------------------------------------------------------
# Synthetic demo cases — all values are obviously fictitious
# ---------------------------------------------------------------------------
DEMO_CASES = [
    {
        "case_ref": "DEMO-CASE-001",
        "demo_patient_name": "SYNTHETIC PATIENT ALPHA",
        "demo_beneficiary_id": "DEMO-BEN-00001",
        "demo_dob": date(1985, 6, 15),
        "demo_gender": "Male",
        "demo_hospital_name": "Demo General Hospital",
        "demo_hospital_code": "DEMO-HOSP-001",
        "demo_procedure_name": "Demo Procedure — Appendectomy",
        "demo_procedure_code": "DEMO-PROC-0042",
        "demo_amount": 25000.00,
        "demo_documents": json.dumps(
            ["demo_discharge_summary.pdf", "demo_id_proof.pdf", "demo_prescription.pdf"]
        ),
    },
    {
        "case_ref": "DEMO-CASE-002",
        "demo_patient_name": "SYNTHETIC PATIENT BETA",
        "demo_beneficiary_id": "DEMO-BEN-00002",
        "demo_dob": date(1972, 11, 3),
        "demo_gender": "Female",
        "demo_hospital_name": "Demo General Hospital",
        "demo_hospital_code": "DEMO-HOSP-001",
        "demo_procedure_name": "Demo Procedure — Cataract Surgery",
        "demo_procedure_code": "DEMO-PROC-0087",
        "demo_amount": 12000.00,
        "demo_documents": json.dumps(["demo_discharge_summary.pdf", "demo_eye_report.pdf"]),
    },
    {
        "case_ref": "DEMO-CASE-003",
        "demo_patient_name": "SYNTHETIC PATIENT GAMMA",
        "demo_beneficiary_id": "DEMO-BEN-00003",
        "demo_dob": date(1990, 3, 22),
        "demo_gender": "Female",
        "demo_hospital_name": "Demo General Hospital",
        "demo_hospital_code": "DEMO-HOSP-001",
        "demo_procedure_name": "Demo Procedure — Maternity Package",
        "demo_procedure_code": "DEMO-PROC-0121",
        "demo_amount": 9000.00,
        "demo_documents": json.dumps(["demo_discharge_summary.pdf", "demo_maternity_record.pdf"]),
    },
]


async def seed_demo_data(db: AsyncSession) -> None:
    """
    Create demo organization, user, and cases if they don't already exist.
    Safe to call multiple times (idempotent).
    """
    # Check if already seeded
    existing_org = await db.execute(select(Organization).where(Organization.slug == DEMO_ORG_SLUG))
    org = existing_org.scalar_one_or_none()

    if not org:
        logger.info("Seeding demo organization and data...")
        org = Organization(
            id=uuid.uuid4(),
            name=DEMO_ORG_NAME,
            slug=DEMO_ORG_SLUG,
            is_active=True,
        )
        db.add(org)
        await db.flush()  # get org.id

        # Demo user
        user = User(
            id=uuid.uuid4(),
            organization_id=org.id,
            email=DEMO_USER_EMAIL,
            hashed_password=hash_password(DEMO_USER_PASSWORD),
            full_name=DEMO_USER_NAME,
            is_active=True,
            is_admin=True,
        )
        db.add(user)

        # Demo cases
        for case_data in DEMO_CASES:
            case = DemoCase(
                id=uuid.uuid4(),
                organization_id=org.id,
                demo_is_synthetic=True,
                is_active=True,
                **case_data,
            )
            db.add(case)

        await db.commit()
        logger.info("Demo data seeded. Login: %s / %s", DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    else:
        logger.debug("Demo data already exists — skipping seed")
