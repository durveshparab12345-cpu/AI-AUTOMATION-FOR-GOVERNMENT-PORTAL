"""stage_2a_organizations_users_demo_cases_executions

Revision ID: 2dd10dd617f3
Revises:
Create Date: 2026-09-28

Creates:
  - organizations
  - users
  - demo_cases
  - automation_executions
  - automation_execution_steps
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "2dd10dd617f3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- organizations ---
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_organization_id", "users", ["organization_id"])

    # --- demo_cases ---
    op.create_table(
        "demo_cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_ref", sa.String(50), nullable=False),
        sa.Column("demo_patient_name", sa.String(255), nullable=False),
        sa.Column("demo_beneficiary_id", sa.String(100), nullable=False),
        sa.Column("demo_dob", sa.Date(), nullable=False),
        sa.Column("demo_gender", sa.String(20), nullable=False),
        sa.Column("demo_hospital_name", sa.String(255), nullable=False),
        sa.Column("demo_hospital_code", sa.String(50), nullable=False),
        sa.Column("demo_procedure_name", sa.String(255), nullable=False),
        sa.Column("demo_procedure_code", sa.String(50), nullable=False),
        sa.Column("demo_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("demo_documents", sa.Text(), nullable=False, server_default="[]"),
        sa.Column(
            "demo_is_synthetic", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_demo_cases_organization_id", "demo_cases", ["organization_id"])
    op.create_index("ix_demo_cases_case_ref", "demo_cases", ["case_ref"])

    # --- execution status enum ---
    execution_status = postgresql.ENUM(
        "PENDING",
        "RUNNING",
        "WAITING_FOR_HUMAN",
        "VALIDATING",
        "COMPLETED",
        "FAILED",
        "CANCELLED",
        name="execution_status_enum",
    )
    execution_status.create(op.get_bind())

    # --- step status enum ---
    step_status = postgresql.ENUM(
        "PENDING",
        "RUNNING",
        "WAITING_FOR_HUMAN",
        "SUCCESS",
        "FAILED",
        "SKIPPED",
        name="step_status_enum",
    )
    step_status.create(op.get_bind())

    # --- automation_executions ---
    op.create_table(
        "automation_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "demo_case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("demo_cases.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("workflow_name", sa.String(255), nullable=False),
        sa.Column("initiated_by", sa.String(255), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING", "RUNNING", "WAITING_FOR_HUMAN", "VALIDATING",
                "COMPLETED", "FAILED", "CANCELLED",
                name="execution_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("current_step", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("waiting_reason", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("portal_result", sa.Text(), nullable=True),
        sa.Column("last_screenshot_path", sa.String(500), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_automation_executions_organization_id",
        "automation_executions",
        ["organization_id"],
    )
    op.create_index(
        "ix_automation_executions_status", "automation_executions", ["status"]
    )

    # --- automation_execution_steps ---
    op.create_table(
        "automation_execution_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "execution_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("automation_executions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(255), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING", "RUNNING", "WAITING_FOR_HUMAN", "SUCCESS", "FAILED", "SKIPPED",
                name="step_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("step_metadata", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_automation_execution_steps_execution_id",
        "automation_execution_steps",
        ["execution_id"],
    )


def downgrade() -> None:
    op.drop_table("automation_execution_steps")
    op.drop_table("automation_executions")
    op.drop_table("demo_cases")
    op.drop_table("users")
    op.drop_table("organizations")

    # Drop enums
    sa.Enum(name="step_status_enum").drop(op.get_bind())
    sa.Enum(name="execution_status_enum").drop(op.get_bind())
