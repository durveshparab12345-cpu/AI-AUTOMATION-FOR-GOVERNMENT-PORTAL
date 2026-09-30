# AI Portal Automation Platform - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Module Relationships](#module-relationships)
3. [Multi-Tenant Architecture](#multi-tenant-architecture)
4. [RBAC and Authorization Flow](#rbac-and-authorization-flow)
5. [Case Lifecycle and State Machine](#case-lifecycle-and-state-machine)
6. [Workflow Engine Architecture](#workflow-engine-architecture)
7. [Execution Engine Architecture](#execution-engine-architecture)
8. [Database Schema Overview](#database-schema-overview)
9. [API Versioning Strategy](#api-versioning-strategy)
10. [Error Handling and Exceptions](#error-handling-and-exceptions)
11. [Audit and Logging Architecture](#audit-and-logging-architecture)
12. [Security Architecture](#security-architecture)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              Web UI for Portal Automation                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────────────┐
│                    FastAPI Backend                           │
│   - API Routes (v1, v2)                                      │
│   - Authentication & Authorization                          │
│   - Business Logic Services                                 │
│   - Workflow Engine                                         │
└──┬──────────────┬──────────────┬──────────────┬─────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────┐   ┌─────────────┐ ┌─────────┐  ┌──────────────┐
│  DB  │   │  Redis      │ │  S3/    │  │  AI          │
│(PG)  │   │  Cache      │ │ Storage │  │  Providers   │
└──────┘   └─────────────┘ └─────────┘  └──────────────┘
   │              ▲
   └──────┬───────┘
          │
    ┌─────▼──────────┐
    │  Celery        │
    │  Workers       │
    │  - Automation  │
    │  - OCR/Doc     │
    │  - Scheduler   │
    └────────────────┘
```

### Key Components

- **API Gateway**: FastAPI with middleware for auth, rate limiting, request tracking
- **Database Layer**: PostgreSQL with SQLAlchemy ORM
- **Cache Layer**: Redis for session storage, caching, rate limiting
- **Task Queue**: Celery for asynchronous processing
- **AI Integration**: Abstract provider layer for OpenAI/Claude/custom models
- **Browser Automation**: Selenium/Playwright for portal interactions
- **File Storage**: Local or S3 for document storage

---

## Module Relationships

### Core Module (`app/core/`)

```
core/
├── config.py           # Configuration management with environment support
├── security.py         # JWT, password hashing, credential management
├── dependencies.py     # FastAPI dependency injection
├── logging.py          # Structured logging with request tracking
├── middleware.py       # Middleware stack (tenant, request ID, rate limit)
└── constants.py        # Enums and application constants
```

**Responsibilities:**
- Global application configuration
- Security utilities (JWT, encryption)
- Dependency resolution for routes
- Request context management
- Standardized exception handling

### API Module (`app/api/`)

```
api/
└── v1/
    ├── auth.py              # Authentication endpoints
    ├── health.py            # Health check
    ├── cases.py             # Case CRUD operations
    ├── beneficiaries.py     # Beneficiary management
    ├── preauth.py           # Pre-authorization workflow
    ├── treatments.py        # Treatment records
    ├── discharges.py        # Discharge management
    ├── claims.py            # Claim processing
    ├── documents.py         # Document upload/processing
    ├── queries.py           # Saved query management
    ├── workflows.py         # Workflow definitions
    ├── executions.py        # Workflow execution control
    ├── users.py             # User management
    ├── organizations.py     # Organization management
    ├── roles.py             # Role and permission management
    └── audit.py             # Audit log queries
```

**Responsibilities:**
- HTTP request/response handling
- Request validation and serialization
- Permission checks via decorators
- Route-specific documentation

### Services Module (`app/services/`)

```
services/
├── auth_service.py              # Authentication logic
├── user_service.py              # User operations
├── role_service.py              # Role and permission logic
├── authorization_service.py     # Permission checking
├── case_service.py              # Case business logic
├── beneficiary_service.py       # Beneficiary operations
├── preauth_service.py           # Pre-auth workflow
├── treatment_service.py         # Treatment operations
├── discharge_service.py         # Discharge operations
├── claim_service.py             # Claim processing
├── document_service.py          # Document handling
├── validation_service.py        # Cross-cutting validation
├── field_mapping_service.py     # Field extraction/mapping
├── query_service.py             # Query building/execution
├── workflow_service.py          # Workflow management
├── workflow_runner.py           # Workflow execution engine
├── execution_service.py         # Execution management
├── audit_service.py             # Audit logging
├── credential_service.py        # Secure credential storage
├── portals/
│   ├── base.py                 # Abstract portal adapter
│   ├── pmjay.py                # PMJAY portal implementation
│   └── adapter_factory.py      # Portal adapter factory
├── browser/
│   ├── browser_manager.py      # Browser instance management
│   ├── browser_session.py      # Session handling
│   ├── actions.py              # Browser automation actions
│   ├── selectors.py            # Portal-specific selectors
│   └── worker.py               # Celery task wrapper
├── ai/
│   ├── base.py                 # Abstract AI provider
│   ├── providers/
│   │   ├── openai_provider.py  # OpenAI integration
│   │   ├── anthropic_provider.py # Claude integration
│   │   └── mock_provider.py    # Testing provider
│   ├── workflow_generator.py   # AI-driven workflow generation
│   ├── document_classifier.py  # Document classification
│   └── field_suggester.py      # Field suggestion/extraction
└── demo_seeder.py              # Demo data population
```

**Responsibilities:**
- Business logic implementation
- Database queries via repositories
- External service integration
- Error handling and validation
- Transaction management

### Models Module (`app/models/`)

Database models using SQLAlchemy ORM:

```
models/
├── base.py                  # BaseModel with audit fields
├── user.py                  # User accounts
├── organization.py          # Tenant organizations
├── role.py                  # Roles for RBAC
├── permission.py            # Permissions
├── role_permission.py       # Many-to-many join table
├── audit_log.py             # Immutable audit trail
├── case.py                  # Healthcare cases
├── beneficiary.py           # Beneficiary information
├── admission.py             # Admission records
├── preauthorization.py      # Pre-auth requests
├── treatment.py             # Treatment records
├── discharge.py             # Discharge records
├── claim.py                 # Insurance claims
├── document.py              # Uploaded documents
├── document_rule.py         # Document validation rules
├── field_definition.py      # Field metadata
├── field_mapping.py         # Field extraction rules
├── query.py                 # Saved queries
├── workflow.py              # Workflow definitions
├── workflow_version.py      # Workflow versions
├── workflow_step.py         # Workflow steps
├── execution.py             # Workflow executions
├── portal.py                # Portal configurations
├── portal_version.py        # Portal versions
├── portal_credential.py     # Portal credentials (encrypted)
├── company_rule.py          # Company-specific rules
└── human_intervention.py    # Human intervention points
```

**Relationships:**
- `User` → `Organization` (many-to-one)
- `User` → `Role` (many-to-many through join table)
- `Role` → `Permission` (many-to-many)
- `Case` → `Beneficiary` (one-to-many)
- `Case` → `Execution` (one-to-many)
- `Workflow` → `WorkflowVersion` (one-to-many)
- `WorkflowVersion` → `WorkflowStep` (one-to-many)
- `Execution` → `Case` (many-to-one)

### Repositories Module (`app/repositories/`)

Data access layer:

```
repositories/
├── base.py                       # BaseRepository with CRUD
├── user_repository.py            # User queries
├── case_repository.py            # Case queries
├── beneficiary_repository.py     # Beneficiary queries
├── preauth_repository.py         # Pre-auth queries
├── treatment_repository.py       # Treatment queries
├── discharge_repository.py       # Discharge queries
├── claim_repository.py           # Claim queries
├── document_repository.py        # Document queries
├── query_repository.py           # Saved query queries
├── workflow_repository.py        # Workflow queries
├── execution_repository.py       # Execution queries
├── audit_log_repository.py       # Audit log queries
├── role_repository.py            # Role queries
└── demo_case_repository.py       # Demo case queries
```

**Responsibilities:**
- Database queries using SQLAlchemy
- Query optimization
- Transaction management
- Pagination and filtering

### Schemas Module (`app/schemas/`)

Pydantic models for validation and serialization:

```
schemas/
├── pagination.py            # PaginatedResponse
├── user.py                  # User request/response
├── role.py                  # Role request/response
├── case.py                  # Case request/response
├── beneficiary.py           # Beneficiary request/response
├── preauth.py               # Pre-auth request/response
├── treatment.py             # Treatment request/response
├── discharge.py             # Discharge request/response
├── claim.py                 # Claim request/response
├── document.py              # Document request/response
├── field_mapping.py         # Field mapping request/response
├── query.py                 # Query request/response
├── workflow.py              # Workflow request/response
├── execution.py             # Execution request/response
└── audit_log.py             # Audit log response
```

**Responsibilities:**
- Request validation
- Response serialization
- Documentation via JSON Schema

### Utils Module (`app/utils/`)

```
utils/
├── decorators.py            # @require_permission, @require_role, etc.
├── validators.py            # Reusable validators
├── crypto.py                # Encryption, hashing, tokens
├── date_utils.py            # Date/time utilities
└── (domain-specific utilities)
```

**Responsibilities:**
- Cross-cutting concerns
- Reusable utilities
- Security operations

### Workers Module (`app/workers/`)

Celery task queue:

```
workers/
├── celery_app.py            # Celery configuration
└── tasks/
    ├── automation_tasks.py  # Portal automation tasks
    ├── document_tasks.py    # OCR, document processing
    ├── notification_tasks.py # Email, notifications
    └── scheduling_tasks.py  # Scheduled tasks
```

**Responsibilities:**
- Asynchronous task execution
- Long-running operations
- Scheduled jobs
- Task monitoring and retry logic

---

## Multi-Tenant Architecture

### Tenant Isolation Strategy

The platform is designed as a true multi-tenant SaaS with complete data isolation:

```
┌─────────────────────────────────────────────┐
│           Request Processing                │
├─────────────────────────────────────────────┤
│  1. Extract tenant_id from JWT or header   │
│  2. Validate tenant ownership               │
│  3. Store in context (request-scoped)       │
│  4. Apply to all database queries           │
│  5. Verify tenant in repository filters     │
└─────────────────────────────────────────────┘
```

### Data Isolation

**Database Level:**
- All tables have `tenant_id` column
- Foreign keys include `tenant_id` in composite keys
- Queries always filter by `tenant_id`
- Indexes on (tenant_id, other_fields)

**Application Level:**
- `TenantContextMiddleware` extracts and validates tenant
- `get_current_tenant()` dependency available to routes
- Repositories enforce tenant filtering
- Services validate tenant ownership

**Query Pattern:**
```python
# Bad - exposes other tenant's data
Case.query.filter_by(case_id=123)

# Good - tenant-aware
Case.query.filter_by(tenant_id=current_tenant, case_id=123)
```

### Tenant Data Flow

```
┌──────────────┐
│  Request     │
│  with JWT    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│ Extract tenant_id from JWT       │
│ Set in ContextVar                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Route Handler receives            │
│ current_tenant dependency         │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Service layer validates tenant    │
│ Repository adds tenant_id filter  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Query: WHERE tenant_id = X       │
│ AND (other filters)              │
└──────────────────────────────────┘
```

---

## RBAC and Authorization Flow

### Permission Model

Role-Based Access Control (RBAC) with resource-action permissions:

```
User
  ├─ roles: List[Role]
  
Role
  ├─ name: str (ADMIN, MANAGER, OPERATOR, VIEWER)
  ├─ permissions: List[Permission]
  └─ tenant_id: str
  
Permission
  ├─ resource: enum (CASE, USER, WORKFLOW, DOCUMENT, etc.)
  ├─ action: enum (CREATE, READ, UPDATE, DELETE, EXECUTE, MANAGE)
  └─ conditions: str (JSON with additional filters)
```

### Authorization Flow

```
┌────────────────────────────────────────┐
│ Request arrives at protected endpoint  │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Extract user from JWT token            │
│ Load user roles and permissions        │
│ Store in context                       │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Check if user has required permission: │
│ resource + action (e.g., CASE:READ)    │
└────────┬─────────────────────────────┘
         │
      ┌──┴──┐
      │     │
      ▼     ▼
    Yes    No
     │      │
     │      └─► 403 Forbidden
     │         (Log to audit)
     │
     ▼
┌────────────────────────────────────────┐
│ Check resource-level permissions       │
│ (if applicable, via service logic)     │
└────────┬─────────────────────────────┘
         │
      ┌──┴──┐
      │     │
      ▼     ▼
    Yes    No
     │      │
     │      └─► 403 Forbidden
     │         (Log to audit)
     │
     ▼
┌────────────────────────────────────────┐
│ Proceed with business logic            │
└────────────────────────────────────────┘
```

### Usage in Code

```python
# Route-level permission check
@router.delete("/cases/{case_id}")
@require_permission("CASE", "DELETE")
async def delete_case(case_id: str):
    # Implementation
    pass

# Service-level permission check
class CaseService:
    def delete_case(self, case_id: str, user: User):
        # Verify user has CASE:DELETE permission
        if not authorization_service.has_permission(
            user, "CASE", "DELETE"
        ):
            raise AuthorizationException(
                "User does not have permission to delete cases"
            )
        # Implementation
        pass
```

### Default Roles

```
SUPER_ADMIN
├─ All permissions on all resources
└─ Tenant administration

ADMIN
├─ CASE: CREATE, READ, UPDATE, DELETE
├─ USER: CREATE, READ, UPDATE, DELETE
├─ WORKFLOW: CREATE, READ, UPDATE, DELETE, EXECUTE
├─ DOCUMENT: READ
└─ AUDIT: READ

MANAGER
├─ CASE: CREATE, READ, UPDATE
├─ USER: READ
├─ WORKFLOW: READ, EXECUTE
├─ DOCUMENT: READ, CREATE
└─ AUDIT: READ

OPERATOR
├─ CASE: CREATE, READ, UPDATE
├─ WORKFLOW: READ, EXECUTE
└─ DOCUMENT: CREATE

VIEWER
├─ CASE: READ
├─ DOCUMENT: READ
└─ AUDIT: READ
```

---

## Case Lifecycle and State Machine

### Case States

```
INITIATED
  ├─ Admission verified
  ▼
ADMISSION_VERIFIED
  ├─ Submit for pre-auth
  ▼
PREAUTH_SUBMITTED
  ├─ Approved
  ├─ Rejected ──► CANCELLED
  │
  ├─ Approved
  ▼
PREAUTH_APPROVED
  ├─ Treatment started
  ▼
TREATMENT_STARTED
  ├─ Progress
  ▼
TREATMENT_IN_PROGRESS
  ├─ Complete treatment
  ▼
TREATMENT_COMPLETED
  ├─ Initiate discharge
  ▼
DISCHARGE_INITIATED
  ├─ Complete discharge
  ▼
DISCHARGE_COMPLETED
  ├─ Submit claim
  ▼
CLAIM_SUBMITTED
  ├─ Approved
  ├─ Rejected ──► (Review)
  │
  ├─ Approved
  ▼
CLAIM_APPROVED
  ├─ Finalize
  ▼
CLOSED
```

### State Transitions

Allowed transitions:
```python
TRANSITIONS = {
    CaseStatus.INITIATED: [CaseStatus.ADMISSION_VERIFIED],
    CaseStatus.ADMISSION_VERIFIED: [CaseStatus.PREAUTH_SUBMITTED],
    CaseStatus.PREAUTH_SUBMITTED: [
        CaseStatus.PREAUTH_APPROVED,
        CaseStatus.PREAUTH_REJECTED,
        CaseStatus.CANCELLED,
    ],
    CaseStatus.PREAUTH_APPROVED: [CaseStatus.TREATMENT_STARTED],
    CaseStatus.TREATMENT_STARTED: [CaseStatus.TREATMENT_IN_PROGRESS],
    CaseStatus.TREATMENT_IN_PROGRESS: [
        CaseStatus.TREATMENT_COMPLETED,
        CaseStatus.TREATMENT_IN_PROGRESS,  # Repetitive state
    ],
    CaseStatus.TREATMENT_COMPLETED: [CaseStatus.DISCHARGE_INITIATED],
    CaseStatus.DISCHARGE_INITIATED: [CaseStatus.DISCHARGE_COMPLETED],
    CaseStatus.DISCHARGE_COMPLETED: [CaseStatus.CLAIM_SUBMITTED],
    CaseStatus.CLAIM_SUBMITTED: [
        CaseStatus.CLAIM_APPROVED,
        CaseStatus.CLAIM_REJECTED,
    ],
    CaseStatus.CLAIM_APPROVED: [CaseStatus.CLOSED],
}
```

### Workflow Triggers

Each state transition can trigger workflows:

```python
state_workflows = {
    CaseStatus.PREAUTH_SUBMITTED: "pmjay_preauth_workflow",
    CaseStatus.TREATMENT_STARTED: "treatment_monitoring_workflow",
    CaseStatus.DISCHARGE_INITIATED: "discharge_workflow",
    CaseStatus.CLAIM_SUBMITTED: "claim_submission_workflow",
}
```

---

## Workflow Engine Architecture

### Workflow Structure

```
Workflow (Definition)
├─ name: str
├─ version: int
├─ tenant_id: str
├─ status: enum (DRAFT, ACTIVE, INACTIVE, ARCHIVED)
├─ steps: List[WorkflowStep]
└─ metadata: JSON
    ├─ description
    ├─ tags
    └─ triggers

WorkflowStep
├─ order: int
├─ type: enum (AUTOMATION, DECISION, NOTIFICATION, HUMAN_INTERVENTION)
├─ name: str
├─ action: str (AI-generated, browser automation, etc.)
├─ conditions: JSON
├─ retry_policy: JSON
├─ timeout: int
├─ next_steps: List[NextStep]
│   ├─ on_success: str (next step ID)
│   └─ on_failure: str (fallback step)
└─ payload: JSON
```

### Workflow Execution Flow

```
┌─────────────────────────────────┐
│ Workflow Triggered              │
│ (case state change, schedule)   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Create Execution record         │
│ Status = PENDING                │
│ Store case_id, workflow_id      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Get first WorkflowStep          │
│ Load step configuration         │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Evaluate conditions             │
│ Load context data               │
└────────┬────────────────────────┘
         │
      ┌──┴──┐
      │     │
      ▼     ▼
   True   False
    │      │
    │      └─► Skip to next_steps.on_failure
    │
    ▼
┌─────────────────────────────────┐
│ Execute Step (based on type)    │
│ - AUTOMATION: run action        │
│ - DECISION: evaluate logic      │
│ - NOTIFICATION: send message    │
│ - HUMAN: pause execution        │
└────────┬────────────────────────┘
         │
      ┌──┴──┐
      │     │
      ▼     ▼
 Success  Failure
   │        │
   │        └─► Apply retry_policy
   │            If retries exhausted
   │            └─► on_failure path
   │
   ▼
┌─────────────────────────────────┐
│ Get next step from transitions  │
│ Loop to step execution          │
└────────┬────────────────────────┘
         │
         ▼ (No next step or end marker)
┌─────────────────────────────────┐
│ Update Execution Status         │
│ COMPLETED or FAILED             │
│ Record end_time                 │
└─────────────────────────────────┘
```

### Step Types

**AUTOMATION**: Execute programmatic action
```python
{
    "type": "AUTOMATION",
    "action": "fill_form_field",
    "payload": {
        "field": "beneficiary_name",
        "value": "{{ case.beneficiary.name }}",
        "provider": "browser"
    }
}
```

**DECISION**: Branch based on condition
```python
{
    "type": "DECISION",
    "conditions": {
        "if": "{{ case.preauth_status }} == 'APPROVED'",
        "then": "step_id_5",
        "else": "step_id_8"
    }
}
```

**NOTIFICATION**: Send notification
```python
{
    "type": "NOTIFICATION",
    "action": "send_email",
    "payload": {
        "to": "{{ case.hospital_email }}",
        "subject": "Case {{ case.id }} approved",
        "template": "case_approved"
    }
}
```

**HUMAN_INTERVENTION**: Pause for manual action
```python
{
    "type": "HUMAN_INTERVENTION",
    "reason": "Manual verification required",
    "assigned_to": "manager_role",
    "timeout": 3600,
    "actions": ["approve", "reject", "need_info"]
}
```

---

## Execution Engine Architecture

### Execution States

```
PENDING → RUNNING → COMPLETED
           ├─→ PAUSED → RUNNING
           ├─→ FAILED
           ├─→ CANCELLED
           └─→ HUMAN_INTERVENTION_REQUIRED → RUNNING (after resolution)
```

### Execution Tracking

```
Execution
├─ id: str
├─ workflow_id: str
├─ case_id: str
├─ status: enum
├─ started_at: datetime
├─ ended_at: datetime
├─ current_step: int
├─ step_executions: List[StepExecution]
├─ context: JSON (runtime data)
├─ error: str (if failed)
└─ audit_logs: List[str]

StepExecution
├─ step_id: str
├─ order: int
├─ status: enum (PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
├─ started_at: datetime
├─ ended_at: datetime
├─ input: JSON
├─ output: JSON
├─ error: str (if failed)
└─ retry_count: int
```

### Runtime Context

Execution context available to steps:

```python
context = {
    "execution_id": "exec-123",
    "workflow_id": "workflow-456",
    "case_id": "case-789",
    "case": {...},  # Full case data
    "beneficiary": {...},  # Beneficiary data
    "user": {...},  # Current user
    "tenant_id": "tenant-001",
    "step_results": {...},  # Results from previous steps
    "env": {...},  # Environment variables
}
```

### Error Handling in Execution

```python
retry_policy = {
    "max_retries": 3,
    "backoff_multiplier": 2,
    "initial_delay_seconds": 1,
    "max_delay_seconds": 60,
}

error_handling = {
    "on_failure": "skip_to_step_id",  # or "pause" or "cancel"
    "notify_on_failure": True,
    "log_details": True,
}
```

---

## Database Schema Overview

### Core Tables

**users**
```sql
id, tenant_id, email, password_hash, first_name, last_name,
is_active, created_at, updated_at, created_by, updated_by, deleted_at
```

**organizations**
```sql
id, name, industry, country, max_users, subscription_tier,
api_key_hash, webhook_url, settings_json,
created_at, updated_at, created_by, updated_by
```

**roles**
```sql
id, tenant_id, name, description, is_system,
created_at, updated_at, created_by, updated_by
```

**permissions**
```sql
id, resource, action, description,
created_at, updated_at
```

**role_permissions**
```sql
id, role_id, permission_id, conditions_json,
created_at
```

**user_roles**
```sql
id, user_id, role_id,
created_at, deleted_at
```

**cases**
```sql
id, tenant_id, case_number, status, beneficiary_id, admission_id,
preauth_id, treatment_id, discharge_id, claim_id,
created_at, updated_at, created_by, updated_by,
is_archived, notes
```

**beneficiaries**
```sql
id, tenant_id, aadhar, name, dob, gender, contact_number,
address, relation_to_primary, primary_member_id,
created_at, updated_at, created_by, updated_by
```

**preauthorizations**
```sql
id, tenant_id, case_id, status, amount_requested, amount_approved,
hospital_id, procedure_codes, valid_from, valid_till,
created_at, updated_at, created_by, updated_by
```

**claims**
```sql
id, tenant_id, case_id, status, amount_claimed, amount_approved,
claim_number, submission_date, approval_date,
created_at, updated_at, created_by, updated_by
```

**documents**
```sql
id, tenant_id, case_id, type, status, original_filename, storage_path,
file_size, mime_type, uploaded_by, processing_status,
extracted_fields_json, classification, confidence_score,
created_at, updated_at, created_by, updated_at
```

**workflows**
```sql
id, tenant_id, name, description, status, version, trigger_type,
steps_json, metadata_json, is_locked,
created_at, updated_at, created_by, updated_by, published_at
```

**executions**
```sql
id, tenant_id, workflow_id, case_id, status, current_step,
context_json, started_at, ended_at, completed_at,
error_message, created_at, updated_at
```

**audit_logs**
```sql
id, tenant_id, user_id, action, resource_type, resource_id,
old_values_json, new_values_json, request_id,
status, error_message, ip_address,
created_at (immutable)
```

---

## API Versioning Strategy

### Versioning Approach

**URL-based versioning:** `/api/v1/`, `/api/v2/`

```
api/
├── v1/
│   ├── cases.py (endpoints)
│   ├── auth.py
│   ├── workflows.py
│   └── ...
├── v2/ (future)
│   ├── cases.py (new implementation)
│   ├── auth.py
│   └── ...
└── deprecated/
    └── legacy.py
```

### Compatibility Management

**Breaking Changes:**
- Major version increment (v1 → v2)
- Parallel support (6-12 months deprecation)
- Migration guide for clients

**Non-Breaking Changes:**
- Same version
- Optional new fields with defaults
- New endpoints at same version

**Deprecation Policy:**
```python
from fastapi import deprecated

@router.get("/cases/{case_id}")
@deprecated(
    deprecated_in="v1.5",
    removed_in="v2",
    alternative="/api/v2/cases/{case_id}"
)
async def get_case_legacy(case_id: str):
    pass
```

### Response Format

All responses follow consistent format:

```json
{
    "success": true,
    "data": {...},
    "metadata": {
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123456"
    },
    "errors": null
}
```

Error response:
```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "details": [...]
    },
    "metadata": {
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123456"
    }
}
```

---

## Error Handling and Exceptions

### Exception Hierarchy

```
AIPortalException (Base)
├─ AuthenticationException
├─ AuthorizationException
├─ ValidationException
├─ ResourceNotFoundException
├─ DatabaseException
├─ WorkflowException
├─ PortalException
├─ TenantException
├─ ConfigurationException
├─ AuditException
├─ CredentialException
├─ RateLimitException
├─ DocumentException
└─ AIProviderException
```

### Exception Handling Flow

```python
try:
    # Business logic
    case_service.create_case(case_data, user)
except ValidationException as e:
    # 422 Unprocessable Entity
    return error_response(422, e.error_code, str(e))
except AuthorizationException as e:
    # 403 Forbidden
    return error_response(403, e.error_code, str(e))
    # Log to audit
except ResourceNotFoundException as e:
    # 404 Not Found
    return error_response(404, e.error_code, str(e))
except DatabaseException as e:
    # 500 Internal Server Error
    logger.error(f"Database error: {e}")
    return error_response(500, "DATABASE_ERROR", "Internal server error")
except AIPortalException as e:
    # Generic handler
    logger.error(f"Application error: {e}")
    return error_response(500, e.error_code, str(e))
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return error_response(500, "INTERNAL_ERROR", "Internal server error")
```

---

## Audit and Logging Architecture

### Audit Trail

All data changes are logged to immutable `audit_logs` table:

```python
audit_log = {
    "id": "audit-123",
    "tenant_id": "tenant-001",
    "user_id": "user-456",
    "action": "UPDATE",
    "resource_type": "CASE",
    "resource_id": "case-789",
    "old_values": {"status": "INITIATED"},
    "new_values": {"status": "ADMISSION_VERIFIED"},
    "request_id": "req-xyz123",
    "status": "SUCCESS",
    "error_message": null,
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### Audit Events

**System Events:**
- LOGIN, LOGOUT
- PERMISSION_DENIED
- API_RATE_LIMIT_EXCEEDED
- DATABASE_ERROR
- CONFIGURATION_CHANGE

**Data Events:**
- CREATE, READ, UPDATE, DELETE
- BULK_IMPORT, BULK_DELETE
- DATA_EXPORT
- RESTORE_FROM_ARCHIVE

**Business Events:**
- WORKFLOW_EXECUTION
- CASE_STATUS_CHANGE
- PREAUTH_SUBMISSION
- CLAIM_SUBMISSION

**Access Events:**
- CREDENTIAL_ACCESS
- SENSITIVE_DATA_ACCESS
- ADMIN_FUNCTION_CALL

### Logging Architecture

**Structured Logging:**
```python
logger.info(
    "Case created",
    extra={
        "request_id": request_id,
        "tenant_id": tenant_id,
        "case_id": case_id,
        "user_id": user_id,
        "action": "CREATE",
        "resource": "CASE",
    }
)
```

**Log Levels:**
- DEBUG: Development debugging
- INFO: Standard operations
- WARNING: Recoverable issues
- ERROR: Errors requiring attention
- CRITICAL: System failures

---

## Security Architecture

### Authentication

**JWT Token Structure:**
```json
{
    "sub": "user_id",
    "tenant_id": "org_id",
    "email": "user@example.com",
    "roles": ["MANAGER", "OPERATOR"],
    "permissions": ["CASE:READ", "CASE:CREATE"],
    "iat": 1234567890,
    "exp": 1234571490,
    "iss": "https://aiportal.example.com",
    "aud": "https://aiportal.example.com"
}
```

### Data Encryption

**At Rest:**
- Portal credentials encrypted with AES-256-GCM
- Encryption key rotated quarterly
- Old keys retained for decryption of historical data

**In Transit:**
- TLS 1.2+ enforced
- HSTS headers enabled
- Certificate pinning for critical endpoints

### Input Validation

**Levels:**
1. Schema validation (Pydantic)
2. Business rule validation (Services)
3. SQL parameterization (SQLAlchemy ORM)
4. Output encoding (JSON serialization)

### Rate Limiting

```python
rate_limits = {
    "auth_login": "5 requests per 5 minutes per IP",
    "api_general": "1000 requests per hour per user",
    "document_upload": "100 files per day per user",
    "workflow_execution": "100 executions per day per tenant",
}
```

### CORS Policy

```python
cors_config = {
    "allowed_origins": ["https://yourdomain.com"],
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["X-Request-ID"],
    "max_age": 600,
}
```

---

## Deployment Architecture

### Environment Configuration

Environments: **Development**, **Staging**, **Production**

Configuration hierarchy:
1. Default values in code
2. Environment variables override
3. YAML config files override
4. Database configuration override

### Database Migrations

**Tool:** Alembic

Workflow:
```bash
# Create migration
alembic revision -m "Add new field to cases"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Monitoring and Observability

**Metrics:**
- API response times
- Error rates
- Workflow execution success rates
- Database query performance
- Cache hit rates

**Tracing:**
- Request ID propagated through logs
- Distributed tracing with spans
- Execution timeline visualization

**Alerting:**
- High error rates
- Slow queries
- Workflow failures
- Resource exhaustion

---

## Performance Considerations

### Database Optimization

- Indexes on frequently queried fields
- Composite indexes for multi-field filters
- Query result caching with Redis
- Connection pooling

### API Performance

- Pagination for large result sets
- Selective field loading
- Response compression
- CDN for static assets

### Background Processing

- Long-running operations via Celery
- Task prioritization
- Retry with exponential backoff
- Dead letter queue for failed tasks

---

## Testing Strategy

### Test Pyramid

```
         /\
        /  \  E2E Tests
       /    \
      /------\
     /        \ Integration Tests
    /          \
   /-----------\
  /             \ Unit Tests
 /______________\
```

### Critical Test Areas

- **Multi-tenant isolation** - Cross-tenant data access prevention
- **RBAC** - Permission enforcement
- **State transitions** - Case workflow validity
- **Audit logging** - All changes tracked
- **Data encryption** - Sensitive data protection

---

## Development Workflow

### Branching Strategy

```
main
  ├─ develop (integration branch)
  │   ├─ feature/case-management
  │   ├─ feature/workflow-engine
  │   ├─ bugfix/auth-issue
  │   └─ hotfix/security-patch
  │
  └─ staging (pre-production)
```

### Code Quality

- Linting: ruff
- Type checking: mypy
- Testing: pytest
- Coverage: >80% target

---

## Glossary

| Term | Definition |
|------|-----------|
| Case | A healthcare claim/reimbursement request for a beneficiary |
| Beneficiary | Insurance policy holder |
| Pre-auth | Pre-authorization for treatment |
| Workflow | Sequence of automated/manual steps |
| Execution | Runtime instance of a workflow |
| Tenant | An independent organization/customer |
| RBAC | Role-Based Access Control |
| Portal | External system (e.g., PMJAY portal) |
| Audit Log | Immutable record of all data changes |

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Status:** Production Ready
