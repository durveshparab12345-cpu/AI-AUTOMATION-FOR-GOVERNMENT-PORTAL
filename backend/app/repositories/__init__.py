"""Repositories package - data access layer."""

from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.base import BaseRepository
from app.repositories.case_repository import CaseRepository
from app.repositories.demo_case_repository import DemoCaseRepository
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository

# New repositories for Phase 2
from app.repositories.portal_repository import PortalRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.automation_repository import AutomationRepository
from app.repositories.automation_step_repository import AutomationStepRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.field_mapping_repository import FieldMappingRepository
from app.repositories.query_repository import QueryRepository
from app.repositories.human_intervention_repository import HumanInterventionRepository
from app.repositories.exception_repository import ExceptionRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.report_repository import ReportRepository

__all__ = [
    # Phase 1 repositories
    "AuditLogRepository",
    "BaseRepository",
    "CaseRepository",
    "DemoCaseRepository",
    "ExecutionRepository",
    "PermissionRepository",
    "RoleRepository",
    "UserRepository",
    # Phase 2 repositories
    "PortalRepository",
    "WorkflowRepository",
    "AutomationRepository",
    "AutomationStepRepository",
    "DocumentRepository",
    "FieldMappingRepository",
    "QueryRepository",
    "HumanInterventionRepository",
    "ExceptionRepository",
    "NotificationRepository",
    "ReportRepository",
]
