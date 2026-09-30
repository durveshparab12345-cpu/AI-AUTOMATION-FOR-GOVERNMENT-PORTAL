"""phase_1_rbac_audit_case_beneficiary

Revision ID: 3ea2ff8b9c4d
Revises: 2dd10dd617f3
Create Date: 2026-09-28

Creates Phase 1 production foundation:
  - Role-based access control (roles, permissions, join tables)
  - Audit logging (immutable audit trail)
  - Real case engine (cases, beneficiaries)
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "3ea2ff8b9c4d"
down_revision: Union[str, None] = "2dd10dd617f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- roles ---
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
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
    )
    op.create_index("ix_roles_organization_id", "roles", ["organization_id"])
    op.create_index("ix_roles_name", "roles", ["name"])

    # --- permissions ---
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resource", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("resource", "action", name="uq_resource_action"),
    )
    op.create_index("ix_permissions_resource", "permissions", ["resource"])
    op.create_index("ix_permissions_action", "permissions", ["action"])

    # --- role_permissions (join table) ---
    op.create_table(
        "role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("grant_scope", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )
    op.create_index("ix_role_permissions_role_id", "role_permissions", ["role_id"])
    op.create_index("ix_role_permissions_permission_id", "role_permissions", ["permission_id"])

    # --- user_roles (join table) ---
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )
    op.create_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_values", postgresql.JSON(none_as_null=True), nullable=True),
        sa.Column("new_values", postgresql.JSON(none_as_null=True), nullable=True),
        sa.Column("request_id", sa.String(50), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="SUCCESS"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("idx_audit_tenant_resource", "audit_logs",
                    ["organization_id", "resource_type", "resource_id"])
    op.create_index("idx_audit_user", "audit_logs", ["user_id"])
    op.create_index("idx_audit_timestamp", "audit_logs", ["created_at"])
    op.create_index("idx_audit_action", "audit_logs", ["action"])
    op.create_index("idx_audit_request_id", "audit_logs", ["request_id"])

    # --- Create enums for Case and Beneficiary ---
    case_status_enum = postgresql.ENUM(
        "INITIATED",
        "ADMISSION_VERIFIED",
        "PREAUTH_SUBMITTED",
        "PREAUTH_APPROVED",
        "PREAUTH_REJECTED",
        "TREATMENT_STARTED",
        "TREATMENT_IN_PROGRESS",
        "TREATMENT_COMPLETED",
        "DISCHARGE_INITIATED",
        "DISCHARGE_COMPLETED",
        "CLAIM_SUBMITTED",
        "CLAIM_APPROVED",
        "CLAIM_REJECTED",
        "CLOSED",
        "CANCELLED",
        name="case_status_enum",
    )
    case_status_enum.create(op.get_bind())

    case_priority_enum = postgresql.ENUM(
        "LOW",
        "NORMAL",
        "HIGH",
        "CRITICAL",
        name="case_priority_enum",
    )
    case_priority_enum.create(op.get_bind())

    admission_type_enum = postgresql.ENUM(
        "PLANNED",
        "EMERGENCY",
        name="admission_type_enum",
    )
    admission_type_enum.create(op.get_bind())

    gender_enum = postgresql.ENUM(
        "M",
        "F",
        "O",
        name="gender_enum",
    )
    gender_enum.create(op.get_bind())

    relation_type_enum = postgresql.ENUM(
        "PRIMARY",
        "SPOUSE",
        "CHILD",
        "PARENT",
        "SIBLING",
        "OTHER",
        name="relation_type_enum",
    )
    relation_type_enum.create(op.get_bind())

    # --- beneficiaries ---
    op.create_table(
        "beneficiaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pmjay_id", sa.String(50), nullable=False),
        sa.Column("pmjay_family_reference", sa.String(100), nullable=True),
        sa.Column("aadhar_number", sa.String(50), nullable=True),
        sa.Column("voter_id", sa.String(50), nullable=True),
        sa.Column("pan_number", sa.String(50), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column(
            "gender",
            postgresql.ENUM("M", "F", "O", name="gender_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=True),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column(
            "relation_to_primary",
            postgresql.ENUM(
                "PRIMARY", "SPOUSE", "CHILD", "PARENT", "SIBLING", "OTHER",
                name="relation_type_enum", create_type=False
            ),
            nullable=True,
        ),
        sa.Column(
            "primary_beneficiary_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("beneficiaries.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("notes", sa.Text(), nullable=True),
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
    )
    op.create_index("idx_beneficiary_org", "beneficiaries", ["organization_id"])
    op.create_index("idx_beneficiary_pmjay", "beneficiaries", ["pmjay_id"])
    op.create_index("idx_beneficiary_aadhar", "beneficiaries", ["aadhar_number"])

    # --- cases ---
    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_reference", sa.String(50), nullable=False),
        sa.Column(
            "beneficiary_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("beneficiaries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hospital_name", sa.String(255), nullable=False),
        sa.Column("hospital_code", sa.String(50), nullable=True),
        sa.Column(
            "admission_type",
            postgresql.ENUM("PLANNED", "EMERGENCY", name="admission_type_enum", create_type=False),
            nullable=False,
            server_default="PLANNED",
        ),
        sa.Column("admission_date", sa.Date(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "INITIATED",
                "ADMISSION_VERIFIED",
                "PREAUTH_SUBMITTED",
                "PREAUTH_APPROVED",
                "PREAUTH_REJECTED",
                "TREATMENT_STARTED",
                "TREATMENT_IN_PROGRESS",
                "TREATMENT_COMPLETED",
                "DISCHARGE_INITIATED",
                "DISCHARGE_COMPLETED",
                "CLAIM_SUBMITTED",
                "CLAIM_APPROVED",
                "CLAIM_REJECTED",
                "CLOSED",
                "CANCELLED",
                name="case_status_enum",
                create_type=False,
            ),
            nullable=False,
            server_default="INITIATED",
        ),
        sa.Column(
            "priority",
            postgresql.ENUM("LOW", "NORMAL", "HIGH", "CRITICAL", name="case_priority_enum", create_type=False),
            nullable=False,
            server_default="NORMAL",
        ),
        sa.Column("primary_diagnosis_code", sa.String(50), nullable=True),
        sa.Column("primary_diagnosis_description", sa.Text(), nullable=True),
        sa.Column("secondary_diagnosis_codes", postgresql.JSON(none_as_null=True), nullable=False, server_default="[]"),
        sa.Column("primary_procedure_code", sa.String(50), nullable=True),
        sa.Column("primary_procedure_description", sa.Text(), nullable=True),
        sa.Column("secondary_procedure_codes", postgresql.JSON(none_as_null=True), nullable=False, server_default="[]"),
        sa.Column("estimated_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("approved_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("actual_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("preauth_reference", sa.String(100), nullable=True),
        sa.Column("preauth_approved_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("claim_reference", sa.String(100), nullable=True),
        sa.Column("claim_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("claim_approved_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("discharge_date", sa.Date(), nullable=True),
        sa.Column("discharge_type", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("case_metadata", postgresql.JSON(none_as_null=True), nullable=False, server_default="{}"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    )
    op.create_index("idx_case_org", "cases", ["organization_id"])
    op.create_index("idx_case_status", "cases", ["status"])
    op.create_index("idx_case_beneficiary", "cases", ["beneficiary_id"])
    op.create_index("idx_case_created", "cases", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_case_created", table_name="cases")
    op.drop_index("idx_case_beneficiary", table_name="cases")
    op.drop_index("idx_case_status", table_name="cases")
    op.drop_index("idx_case_org", table_name="cases")
    op.drop_table("cases")

    op.drop_index("idx_beneficiary_aadhar", table_name="beneficiaries")
    op.drop_index("idx_beneficiary_pmjay", table_name="beneficiaries")
    op.drop_index("idx_beneficiary_org", table_name="beneficiaries")
    op.drop_table("beneficiaries")

    op.drop_index("idx_audit_request_id", table_name="audit_logs")
    op.drop_index("idx_audit_action", table_name="audit_logs")
    op.drop_index("idx_audit_timestamp", table_name="audit_logs")
    op.drop_index("idx_audit_user", table_name="audit_logs")
    op.drop_index("idx_audit_tenant_resource", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_index("ix_user_roles_user_id", table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index("ix_role_permissions_permission_id", table_name="role_permissions")
    op.drop_index("ix_role_permissions_role_id", table_name="role_permissions")
    op.drop_table("role_permissions")

    op.drop_index("ix_permissions_action", table_name="permissions")
    op.drop_index("ix_permissions_resource", table_name="permissions")
    op.drop_table("permissions")

    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_index("ix_roles_organization_id", table_name="roles")
    op.drop_table("roles")

    # Drop enums
    sa.Enum(name="relation_type_enum").drop(op.get_bind())
    sa.Enum(name="gender_enum").drop(op.get_bind())
    sa.Enum(name="admission_type_enum").drop(op.get_bind())
    sa.Enum(name="case_priority_enum").drop(op.get_bind())
    sa.Enum(name="case_status_enum").drop(op.get_bind())
