"""
Application constants, enums, and application-wide settings.

This module centralizes all enums and constants to avoid magic strings
and enable type-safe comparisons throughout the application.
"""

from enum import Enum


# ============================================================================
# ENVIRONMENTS
# ============================================================================

class Environment(str, Enum):
    """Application deployment environments."""

    DEVELOPMENT = "development"
    TEST = "test"
    DEMO = "demo"
    PRODUCTION = "production"


# ============================================================================
# ROLES
# ============================================================================

class RoleName(str, Enum):
    """Pre-defined system roles."""

    SUPER_ADMIN = "SUPER_ADMIN"  # Full system access
    ADMIN = "ADMIN"              # Organization admin
    MANAGER = "MANAGER"          # Team lead/manager
    OPERATOR = "OPERATOR"        # Portal operator
    VIEWER = "VIEWER"            # Read-only access
    PMAM = "PMAM"                # PM-JAY PMAM role
    MEDCO = "MEDCO"              # PM-JAY MEDCO role
    PREAUTH_REVIEWER = "PREAUTH_REVIEWER"  # Pre-auth review
    CLAIM_EXECUTIVE = "CLAIM_EXECUTIVE"    # Claim executive


DEFAULT_SYSTEM_ROLES = [
    RoleName.SUPER_ADMIN,
    RoleName.ADMIN,
    RoleName.MANAGER,
    RoleName.OPERATOR,
    RoleName.VIEWER,
]

PM_JAY_ROLES = [
    RoleName.PMAM,
    RoleName.MEDCO,
    RoleName.PREAUTH_REVIEWER,
    RoleName.CLAIM_EXECUTIVE,
]


# ============================================================================
# RESOURCES & ACTIONS (for RBAC)
# ============================================================================

class ResourceType(str, Enum):
    """Resource types for permission model."""

    USER = "USER"
    ROLE = "ROLE"
    ORGANIZATION = "ORGANIZATION"
    CASE = "CASE"
    BENEFICIARY = "BENEFICIARY"
    ADMISSION = "ADMISSION"
    PREAUTH = "PREAUTH"
    TREATMENT = "TREATMENT"
    DISCHARGE = "DISCHARGE"
    CLAIM = "CLAIM"
    DOCUMENT = "DOCUMENT"
    DOCUMENT_RULE = "DOCUMENT_RULE"
    WORKFLOW = "WORKFLOW"
    EXECUTION = "EXECUTION"
    FIELD_MAPPING = "FIELD_MAPPING"
    COMPANY_RULE = "COMPANY_RULE"
    QUERY = "QUERY"
    AUDIT_LOG = "AUDIT_LOG"
    PORTAL = "PORTAL"


class ActionType(str, Enum):
    """Action types for permission model."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"
    MANAGE = "MANAGE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


# ============================================================================
# CASE LIFECYCLE STATES
# ============================================================================

class CaseStatus(str, Enum):
    """Case state machine - all possible states."""

    INITIATED = "INITIATED"
    ADMISSION_VERIFIED = "ADMISSION_VERIFIED"
    PREAUTH_SUBMITTED = "PREAUTH_SUBMITTED"
    PREAUTH_APPROVED = "PREAUTH_APPROVED"
    PREAUTH_REJECTED = "PREAUTH_REJECTED"
    TREATMENT_STARTED = "TREATMENT_STARTED"
    TREATMENT_IN_PROGRESS = "TREATMENT_IN_PROGRESS"
    TREATMENT_COMPLETED = "TREATMENT_COMPLETED"
    DISCHARGE_INITIATED = "DISCHARGE_INITIATED"
    DISCHARGE_COMPLETED = "DISCHARGE_COMPLETED"
    CLAIM_SUBMITTED = "CLAIM_SUBMITTED"
    CLAIM_APPROVED = "CLAIM_APPROVED"
    CLAIM_REJECTED = "CLAIM_REJECTED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


# Valid state transitions (state machine)
CASE_STATE_TRANSITIONS = {
    CaseStatus.INITIATED: [CaseStatus.ADMISSION_VERIFIED],
    CaseStatus.ADMISSION_VERIFIED: [CaseStatus.PREAUTH_SUBMITTED],
    CaseStatus.PREAUTH_SUBMITTED: [
        CaseStatus.PREAUTH_APPROVED,
        CaseStatus.PREAUTH_REJECTED,
        CaseStatus.CANCELLED,
    ],
    CaseStatus.PREAUTH_APPROVED: [CaseStatus.TREATMENT_STARTED],
    CaseStatus.PREAUTH_REJECTED: [CaseStatus.CANCELLED],
    CaseStatus.TREATMENT_STARTED: [CaseStatus.TREATMENT_IN_PROGRESS],
    CaseStatus.TREATMENT_IN_PROGRESS: [
        CaseStatus.TREATMENT_COMPLETED,
        CaseStatus.TREATMENT_IN_PROGRESS,  # Can stay in progress
    ],
    CaseStatus.TREATMENT_COMPLETED: [CaseStatus.DISCHARGE_INITIATED],
    CaseStatus.DISCHARGE_INITIATED: [CaseStatus.DISCHARGE_COMPLETED],
    CaseStatus.DISCHARGE_COMPLETED: [CaseStatus.CLAIM_SUBMITTED],
    CaseStatus.CLAIM_SUBMITTED: [
        CaseStatus.CLAIM_APPROVED,
        CaseStatus.CLAIM_REJECTED,
    ],
    CaseStatus.CLAIM_APPROVED: [CaseStatus.CLOSED],
    CaseStatus.CLAIM_REJECTED: [CaseStatus.CLAIM_SUBMITTED],  # Can resubmit
    CaseStatus.CLOSED: [],  # Terminal state
    CaseStatus.CANCELLED: [],  # Terminal state
}


class CasePriority(str, Enum):
    """Case priority levels."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================================
# WORKFLOW EXECUTION STATES
# ============================================================================

class ExecutionStatus(str, Enum):
    """Workflow execution states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, Enum):
    """Individual workflow step states."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class StepType(str, Enum):
    """Types of workflow steps."""

    AUTOMATION = "AUTOMATION"
    DECISION = "DECISION"
    NOTIFICATION = "NOTIFICATION"
    HUMAN_INTERVENTION = "HUMAN_INTERVENTION"


# ============================================================================
# AUDIT ACTIONS
# ============================================================================

class AuditAction(str, Enum):
    """Types of actions logged to audit trail."""

    # User management
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_RESET = "PASSWORD_RESET"

    # Data operations
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BULK_CREATE = "BULK_CREATE"
    BULK_UPDATE = "BULK_UPDATE"
    BULK_DELETE = "BULK_DELETE"

    # Business operations
    CASE_CREATED = "CASE_CREATED"
    CASE_STATUS_CHANGED = "CASE_STATUS_CHANGED"
    PREAUTH_SUBMITTED = "PREAUTH_SUBMITTED"
    PREAUTH_APPROVED = "PREAUTH_APPROVED"
    PREAUTH_REJECTED = "PREAUTH_REJECTED"
    CLAIM_SUBMITTED = "CLAIM_SUBMITTED"
    CLAIM_APPROVED = "CLAIM_APPROVED"
    CLAIM_REJECTED = "CLAIM_REJECTED"

    # Workflow operations
    WORKFLOW_CREATED = "WORKFLOW_CREATED"
    WORKFLOW_PUBLISHED = "WORKFLOW_PUBLISHED"
    AUTOMATION_STARTED = "AUTOMATION_STARTED"
    AUTOMATION_COMPLETED = "AUTOMATION_COMPLETED"
    AUTOMATION_FAILED = "AUTOMATION_FAILED"

    # Security
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # System
    CONFIGURATION_CHANGED = "CONFIGURATION_CHANGED"
    DATABASE_ERROR = "DATABASE_ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class AuditStatus(str, Enum):
    """Status of audit action."""

    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


# ============================================================================
# DOCUMENT TYPES & REQUIREMENTS
# ============================================================================

class DocumentType(str, Enum):
    """Types of documents."""

    AADHAR = "AADHAR"
    VOTER_ID = "VOTER_ID"
    PAN = "PAN"
    HOSPITAL_REGISTRATION = "HOSPITAL_REGISTRATION"
    TREATMENT_AUTHORIZATION = "TREATMENT_AUTHORIZATION"
    PRF = "PRF"  # Pre-authorization request form
    MEDICAL_REPORT = "MEDICAL_REPORT"
    INVESTIGATION_REPORT = "INVESTIGATION_REPORT"
    DISCHARGE_SUMMARY = "DISCHARGE_SUMMARY"
    ITEMIZED_BILL = "ITEMIZED_BILL"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    """Status of a document."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class DocumentRequirement(str, Enum):
    """Whether a document is required or optional."""

    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    OPTIONAL = "OPTIONAL"


# ============================================================================
# BENEFICIARY & ADMISSION
# ============================================================================

class Gender(str, Enum):
    """Gender values."""

    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class RelationType(str, Enum):
    """Relationship to primary beneficiary."""

    PRIMARY = "PRIMARY"
    SPOUSE = "SPOUSE"
    CHILD = "CHILD"
    PARENT = "PARENT"
    SIBLING = "SIBLING"
    OTHER = "OTHER"


class AdmissionType(str, Enum):
    """Type of hospital admission."""

    PLANNED = "PLANNED"
    EMERGENCY = "EMERGENCY"


class DischargeType(str, Enum):
    """Discharge outcome types."""

    NORMAL = "NORMAL"
    LAMA = "LAMA"  # Left against medical advice
    DAMA = "DAMA"  # Discharged against medical advice
    DEATH = "DEATH"
    REFERRED = "REFERRED"


# ============================================================================
# PREAUTHORIZATION & CLAIMS
# ============================================================================

class PreauthStatus(str, Enum):
    """Pre-authorization status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    QUERY_RAISED = "QUERY_RAISED"
    QUERY_RESOLVED = "QUERY_RESOLVED"


class ClaimStatus(str, Enum):
    """Claim status."""

    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    QUERY_RAISED = "QUERY_RAISED"
    QUERY_RESOLVED = "QUERY_RESOLVED"
    FORWARDED = "FORWARDED"
    ACCOUNT_REVIEW = "ACCOUNT_REVIEW"
    SHA_REVIEW = "SHA_REVIEW"
    SETTLED = "SETTLED"


class QueryStatus(str, Enum):
    """Query status."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESPONDED = "RESPONDED"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"


# ============================================================================
# PORTAL INTEGRATION
# ============================================================================

class PortalStatus(str, Enum):
    """Portal configuration status."""

    DRAFT = "DRAFT"
    CONFIGURED = "CONFIGURED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class PortalEnvironment(str, Enum):
    """Portal environment."""

    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class PortalType(str, Enum):
    """Type of portal."""

    PMJAY = "PMJAY"
    TPA = "TPA"
    INSURANCE = "INSURANCE"
    HOSPITAL = "HOSPITAL"
    BANKING = "BANKING"
    CUSTOM = "CUSTOM"


# ============================================================================
# WORKFLOW STATES
# ============================================================================

class WorkflowStatus(str, Enum):
    """Workflow status."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


# ============================================================================
# API ERROR CODES
# ============================================================================

class ErrorCode(str, Enum):
    """Structured error codes for API responses."""

    # Authentication & Authorization
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    FORBIDDEN = "FORBIDDEN"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    REQUIRED_FIELD_MISSING = "REQUIRED_FIELD_MISSING"

    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"

    # Business logic
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    OPERATION_NOT_PERMITTED = "OPERATION_NOT_PERMITTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

    # Tenant & Multi-tenancy
    TENANT_NOT_FOUND = "TENANT_NOT_FOUND"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    CROSS_TENANT_ACCESS = "CROSS_TENANT_ACCESS"

    # Database
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONSTRAINT_VIOLATION = "DATABASE_CONSTRAINT_VIOLATION"

    # File/Document
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"

    # External services
    PORTAL_ERROR = "PORTAL_ERROR"
    AI_PROVIDER_ERROR = "AI_PROVIDER_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"

    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"

    # Server errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


# ============================================================================
# HTTP STATUS MAPPINGS
# ============================================================================

ERROR_CODE_TO_STATUS = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.INVALID_CREDENTIALS: 401,
    ErrorCode.TOKEN_EXPIRED: 401,
    ErrorCode.PERMISSION_DENIED: 403,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.INVALID_INPUT: 422,
    ErrorCode.REQUIRED_FIELD_MISSING: 422,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.RESOURCE_NOT_FOUND: 404,
    ErrorCode.ALREADY_EXISTS: 409,
    ErrorCode.CONFLICT: 409,
    ErrorCode.INVALID_STATE_TRANSITION: 400,
    ErrorCode.OPERATION_NOT_PERMITTED: 400,
    ErrorCode.INSUFFICIENT_DATA: 400,
    ErrorCode.TENANT_NOT_FOUND: 404,
    ErrorCode.TENANT_MISMATCH: 400,
    ErrorCode.CROSS_TENANT_ACCESS: 403,
    ErrorCode.DATABASE_ERROR: 500,
    ErrorCode.DATABASE_CONSTRAINT_VIOLATION: 409,
    ErrorCode.FILE_NOT_FOUND: 404,
    ErrorCode.FILE_UPLOAD_FAILED: 400,
    ErrorCode.INVALID_FILE_TYPE: 415,
    ErrorCode.FILE_TOO_LARGE: 413,
    ErrorCode.PORTAL_ERROR: 502,
    ErrorCode.AI_PROVIDER_ERROR: 502,
    ErrorCode.EXTERNAL_SERVICE_ERROR: 502,
    ErrorCode.RATE_LIMIT_EXCEEDED: 429,
    ErrorCode.TOO_MANY_REQUESTS: 429,
    ErrorCode.INTERNAL_SERVER_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
}
