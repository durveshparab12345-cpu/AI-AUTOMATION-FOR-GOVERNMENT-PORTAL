"""Models package - all SQLAlchemy ORM models."""

from app.models.audit_log import AuditLog
from app.models.base import BaseModel
from app.models.beneficiary import Beneficiary
from app.models.case import Case
from app.models.demo_case import DemoCase
from app.models.execution import AutomationExecution, AutomationExecutionStep
from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole

# New models for Phase 2
from app.models.portal import Portal
from app.models.portal_version import PortalVersion
from app.models.workflow import Workflow
from app.models.workflow_version import WorkflowVersion
from app.models.workflow_node import WorkflowNode
from app.models.automation import Automation
from app.models.automation_step import AutomationStep
from app.models.document import Document
from app.models.field_mapping import FieldMapping
from app.models.query import Query
from app.models.human_intervention import HumanIntervention
from app.models.exception import Exception as ExceptionModel
from app.models.notification import Notification
from app.models.report import Report

__all__ = [
    # Phase 1 models
    "AuditLog",
    "BaseModel",
    "Beneficiary",
    "Case",
    "DemoCase",
    "AutomationExecution",
    "AutomationExecutionStep",
    "Organization",
    "Permission",
    "Role",
    "RolePermission",
    "User",
    "UserRole",
    # Phase 2 models
    "Portal",
    "PortalVersion",
    "Workflow",
    "WorkflowVersion",
    "WorkflowNode",
    "Automation",
    "AutomationStep",
    "Document",
    "FieldMapping",
    "Query",
    "HumanIntervention",
    "ExceptionModel",
    "Notification",
    "Report",
]
