# ============================================================================
# AI PORTAL AUTOMATION PLATFORM - PRODUCTION FOUNDATION PHASE 1
# ============================================================================
#
# This document tracks the systematic transformation from Stage 2A prototype
# to production-ready enterprise SaaS platform.
#
# CURRENT STATUS: Starting Phase 1 - Production Foundation
#
# ============================================================================

## PHASE 1: PRODUCTION FOUNDATION (Priority 1)
### Objective: Establish core production infrastructure

**CRITICAL ITEMS (must complete):**
- [ ] Enhanced Configuration System with environments
- [ ] RBAC System (Roles & Permissions models + service + middleware)
- [ ] Base Models with Audit Trail
- [ ] Tenant Middleware & Security Headers
- [ ] Real Case Engine (not demo_case)
- [ ] Multi-Tenant Isolation Tests (CRITICAL)
- [ ] RBAC Authorization Tests (CRITICAL)

**SECONDARY ITEMS:**
- [ ] Authentication Enhancement (refresh, logout, password reset)
- [ ] Audit Logging Integration
- [ ] API Response Wrapper
- [ ] Pagination Implementation
- [ ] Database Migrations (Phase 1)

## PHASE 2-7: WORKFLOW, DOCUMENTS, AI, TESTING
(See full plan below)

---

## IMPLEMENTATION STRATEGY

### Approach:
1. **Preserve working prototype functionality** (demo workflows still work)
2. **Add production infrastructure layer** (RBAC, audit, multi-tenant enforcement)
3. **Implement real case engine** (parallel with demo)
4. **Build workflow/document/AI engines** one phase at a time
5. **Comprehensive testing** (especially multi-tenant isolation and RBAC)
6. **Production hardening** (security, performance, monitoring)

### Timeline:
- **Week 1 (Phase 1-3)**: Foundation + Workflows + Documents
- **Week 2 (Phase 4-7)**: Portal + AI + Testing + Deployment

### Risk Mitigation:
- Keep demo mode working for backward compatibility
- Feature flags for production features
- Comprehensive test coverage before activation
- Staged rollout: Development → Staging → Production

---

## DETAILED PHASE BREAKDOWN

### PHASE 1: PRODUCTION FOUNDATION

#### 1.1 Enhanced Configuration System
```
Config Levels (highest priority wins):
1. Environment variables
2. .env file
3. YAML config file (per environment)
4. Code defaults

Environments:
- DEVELOPMENT: Local development, debug on, loose security
- TEST: Unit testing, in-memory SQLite, no external services
- DEMO: Staging, feature preview, demo data
- PRODUCTION: Live system, strict security, monitoring on
```

**Files to create/modify:**
- Modify: `app/core/config.py`
  - Add environment enum
  - Add config validation on startup
  - Add environment-specific overrides
  
**Status:** Not Started

#### 1.2 RBAC System (Roles & Permissions)
```
Models:
- Role (id, tenant_id, name, description, is_system)
- Permission (id, resource, action, description)
- RolePermission (role_id, permission_id, conditions_json)
- UserRole (user_id, role_id) - join table

Default Roles:
- SUPER_ADMIN: All permissions
- ADMIN: Case/User/Workflow CRUD
- MANAGER: Case/Workflow READ/UPDATE
- OPERATOR: Case/Workflow READ/EXECUTE
- VIEWER: Case/Document READ

Authorization Checks:
- Route decorators: @require_permission("RESOURCE", "ACTION")
- Service methods: authorization_service.has_permission()
- Middleware: Tenant context + request ID
```

**Files to create:**
- Create: `app/models/role.py`
- Create: `app/models/permission.py`
- Create: `app/models/role_permission.py`
- Create: `app/models/user_role.py`
- Create: `app/repositories/role_repository.py`
- Create: `app/services/role_service.py`
- Create: `app/services/authorization_service.py`
- Create: `app/utils/decorators.py` (@require_permission, @require_role, @audit_log)
- Create: `app/api/v1/roles.py`

**Files to modify:**
- Modify: `app/models/user.py` (add role_id, is_active)
- Modify: `app/core/dependencies.py` (add auth checks)

**Status:** Not Started

#### 1.3 Base Models with Audit Trail
```
BaseModel:
- id: UUID primary key
- tenant_id: UUID foreign key
- created_at: DateTime (server default = now)
- created_by: UUID (user who created)
- updated_at: DateTime (auto-update)
- updated_by: UUID (user who updated)
- deleted_at: DateTime (soft delete)
- deleted_by: UUID (user who deleted)

AuditLog:
- id: UUID
- tenant_id: UUID
- user_id: UUID
- action: ENUM (CREATE, READ, UPDATE, DELETE)
- resource_type: ENUM (CASE, USER, WORKFLOW, etc.)
- resource_id: UUID
- old_values: JSON
- new_values: JSON
- request_id: str (for request tracing)
- status: ENUM (SUCCESS, FAILURE)
- error_message: str (if failure)
- ip_address: str
- user_agent: str
- created_at: DateTime (immutable)

AuditService:
- log_create(resource_type, resource_id, new_values)
- log_update(resource_type, resource_id, old_values, new_values)
- log_delete(resource_type, resource_id, old_values)
- get_audit_trail(resource_type, resource_id)
```

**Files to create:**
- Create: `app/models/base.py` (BaseModel)
- Create: `app/models/audit_log.py`
- Create: `app/repositories/audit_log_repository.py`
- Create: `app/services/audit_service.py`

**Files to modify:**
- Modify: `app/db/base.py` (export BaseModel)
- Modify: All existing models to inherit from BaseModel

**Status:** Not Started

#### 1.4 Tenant Middleware & Security
```
TenantContextMiddleware:
- Extract tenant_id from JWT
- Validate tenant ownership
- Store in ContextVar for request scope
- Add to logger context
- Reject if missing/invalid

RequestIDMiddleware:
- Generate UUID request_id
- Add to response headers (X-Request-ID)
- Store in logger context
- Pass to audit logs

SecurityHeadersMiddleware:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: (if production)

RateLimitMiddleware:
- Per-IP rate limit for login (5 req/5 min)
- Per-user rate limit for API (1000 req/hour)
- Per-tenant rate limit (5000 req/hour)
- Configurable per environment

ErrorHandlingMiddleware:
- Catch all exceptions
- Convert to structured error response
- Log with request_id and tenant_id
- Return appropriate HTTP status code
```

**Files to create:**
- Create: `app/core/middleware.py`
- Create: `app/core/constants.py` (enums)

**Files to modify:**
- Modify: `app/main.py` (add middleware stack)
- Modify: `app/exceptions.py` (add HTTP status mapping)

**Status:** Not Started

#### 1.5 Real Case Engine Foundation
```
Models:
- Case
  - id, tenant_id, case_number, status, priority
  - created_by, updated_by, deleted_by (audit)
  - beneficiary_id, admission_id, preauth_id, treatment_id, discharge_id, claim_id
  - current_stage: ENUM (14 states)
  - assigned_to: user_id
  - metadata: JSON
  - created_at, updated_at, deleted_at

- Beneficiary
  - id, tenant_id, aadhar, name, dob, gender
  - contact_number, address
  - family_info: JSON
  - created_by, updated_by, deleted_by

Case State Machine:
INITIATED
├─ ADMISSION_VERIFIED (on admission registration)
├─ PREAUTH_SUBMITTED (on preauth initiation)
├─ PREAUTH_APPROVED / PREAUTH_REJECTED / CANCELLED
├─ TREATMENT_STARTED
├─ TREATMENT_IN_PROGRESS
├─ TREATMENT_COMPLETED
├─ DISCHARGE_INITIATED
├─ DISCHARGE_COMPLETED
├─ CLAIM_SUBMITTED
├─ CLAIM_APPROVED / CLAIM_REJECTED
├─ CLOSED / CANCELLED

Allowed Transitions:
- Validated at service layer
- Audit logged on each transition
- Triggers workflows on specific transitions
```

**Files to create:**
- Create: `app/models/case.py`
- Create: `app/models/beneficiary.py`
- Create: `app/repositories/case_repository.py`
- Create: `app/repositories/beneficiary_repository.py`
- Create: `app/services/case_service.py`
- Create: `app/services/beneficiary_service.py`
- Create: `app/schemas/case.py`
- Create: `app/schemas/beneficiary.py`
- Create: `app/api/v1/cases.py`
- Create: `app/api/v1/beneficiaries.py`

**Files to modify:**
- None (parallel with existing demo_case)

**Status:** Not Started

#### 1.6 Database Migrations (Phase 1)
```
Migration 1: RBAC Tables
- roles table
- permissions table
- role_permissions join table
- user_roles join table

Migration 2: Audit Tables
- audit_logs table (immutable)
- Add audit fields to existing tables (user, organization)

Migration 3: Case Tables
- cases table
- beneficiaries table
- Add is_active to users (existing table)
- Add role_id to users (existing table)

Constraints:
- All tables have tenant_id except global tables (permissions)
- Foreign keys: CASCADE on org delete, RESTRICT on case delete (to preserve)
- Indexes on (tenant_id, id), (tenant_id, status), (user_id, role_id)
```

**Files to create:**
- Create: `alembic/versions/[timestamp]_add_rbac_tables.py`
- Create: `alembic/versions/[timestamp]_add_audit_fields.py`
- Create: `alembic/versions/[timestamp]_add_case_tables.py`

**Status:** Not Started

#### 1.7 API Response Wrapper
```
All API responses follow this format:

Success:
{
    "success": true,
    "data": {...},  // or [...] for lists
    "metadata": {
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123456"
    }
}

Error:
{
    "success": false,
    "error": {
        "code": "CASE_NOT_FOUND",
        "message": "Case not found",
        "details": {...}  // optional
    },
    "metadata": {
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123456"
    }
}

Pagination:
{
    "success": true,
    "data": [...],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total": 150,
        "total_pages": 8,
        "has_next": true,
        "has_prev": false
    },
    "metadata": {...}
}
```

**Files to create:**
- Create: `app/schemas/pagination.py`
- Create: `app/schemas/response.py` (wrapper)

**Files to modify:**
- Modify: All API route files to use wrapper

**Status:** Not Started

#### 1.8 Testing Foundation (Phase 1)
```
CRITICAL TESTS:
1. Multi-Tenant Isolation
   - User A cannot list User B's cases
   - User A cannot update User B's cases
   - Query always includes tenant_id filter
   - Cross-tenant access returns 404 (not 403)

2. RBAC Authorization
   - User without CASE:CREATE cannot create case
   - User without CASE:DELETE cannot delete case
   - Roles grant permissions correctly
   - Permission denied logged to audit

3. Case State Machine
   - Valid transitions succeed
   - Invalid transitions fail
   - State transitions logged

4. Audit Logging
   - All CREATE/UPDATE/DELETE logged
   - Old/new values captured
   - User tracked correctly
   - Immutable (cannot update audit logs)

Test Structure:
- Unit tests for service layer
- Integration tests with real database
- Security tests for isolation/RBAC
- E2E tests for user workflows
```

**Files to create:**
- Create: `app/tests/integration/test_multi_tenant_isolation.py` (CRITICAL)
- Create: `app/tests/integration/test_rbac_authorization.py` (CRITICAL)
- Create: `app/tests/integration/test_case_lifecycle.py`
- Create: `app/tests/integration/test_audit_logging.py`
- Create: `app/tests/unit/services/test_case_service.py`
- Create: `app/tests/unit/services/test_authorization_service.py`
- Create: `app/tests/fixtures/auth.py` (test user/role fixtures)
- Create: `app/tests/fixtures/cases.py` (test case fixtures)

**Status:** Not Started

---

## TESTING STRATEGY

### Multi-Tenant Isolation Tests (CRITICAL)

```python
def test_user_cannot_access_other_tenant_case():
    # Create two tenants with users
    tenant_a = create_org("Tenant A")
    tenant_b = create_org("Tenant B")
    
    user_a = create_user(tenant_a, email="user_a@example.com")
    user_b = create_user(tenant_b, email="user_b@example.com")
    
    # User A creates a case in Tenant A
    case_a = create_case(tenant_a, case_number="CASE-001")
    
    # User B tries to access case_a (should fail)
    response = get_case(case_a.id, auth=user_b.token)
    assert response.status_code == 404  # Not 200
    
    # Verify case still exists in Tenant A
    response = get_case(case_a.id, auth=user_a.token)
    assert response.status_code == 200

def test_user_cannot_list_other_tenant_cases():
    # Create two tenants with cases
    tenant_a = create_org()
    tenant_b = create_org()
    
    case_a1 = create_case(tenant_a)
    case_a2 = create_case(tenant_a)
    
    case_b1 = create_case(tenant_b)
    case_b2 = create_case(tenant_b)
    
    user_a = create_user(tenant_a)
    user_b = create_user(tenant_b)
    
    # User A lists cases (should see only A's cases)
    cases_a = list_cases(auth=user_a.token)
    assert len(cases_a) == 2
    assert all(c.id in [case_a1.id, case_a2.id] for c in cases_a)
    
    # User B lists cases (should see only B's cases)
    cases_b = list_cases(auth=user_b.token)
    assert len(cases_b) == 2
    assert all(c.id in [case_b1.id, case_b2.id] for c in cases_b)
```

### RBAC Authorization Tests (CRITICAL)

```python
def test_viewer_cannot_create_case():
    tenant = create_org()
    viewer = create_user(tenant, roles=[VIEWER_ROLE])
    
    response = create_case(
        {"case_number": "CASE-001"},
        auth=viewer.token
    )
    assert response.status_code == 403

def test_operator_can_execute_workflow():
    tenant = create_org()
    operator = create_user(tenant, roles=[OPERATOR_ROLE])
    
    response = execute_workflow(
        workflow_id="wf-123",
        auth=operator.token
    )
    assert response.status_code == 200

def test_permission_denied_logged_to_audit():
    tenant = create_org()
    viewer = create_user(tenant, roles=[VIEWER_ROLE])
    
    create_case(
        {"case_number": "CASE-001"},
        auth=viewer.token
    )  # Should fail
    
    # Check audit log for permission denial
    audit_logs = get_audit_logs(
        resource_type="CASE",
        action="CREATE",
        status="FAILURE"
    )
    assert len(audit_logs) > 0
    assert "permission" in audit_logs[0].error_message.lower()
```

---

## BACKWARD COMPATIBILITY

Keep existing demo code working:
- `app/models/demo_case.py` - unchanged
- `app/api/v1/pmjay_demo.py` - unchanged
- Demo seeding - unchanged

Feature flags:
```python
USE_DEMO_MODE = env("DEMO_MODE", True)

@router.get("/pmjay-demo/cases")  # Old endpoint
@router.get("/api/v1/cases")       # New endpoint
```

Both endpoints work during transition period.

---

## SUCCESS CRITERIA FOR PHASE 1

- [ ] All RBAC models created and tested
- [ ] All RBAC decorators working
- [ ] Multi-tenant isolation enforced at all layers
- [ ] Multi-tenant isolation tests passing (CRITICAL)
- [ ] RBAC authorization tests passing (CRITICAL)
- [ ] Case model implemented with state machine
- [ ] Case API endpoints working (CRUD + timeline)
- [ ] Audit logging working for all changes
- [ ] Middleware stack integrated
- [ ] Configuration system supporting environments
- [ ] All migrations applied cleanly
- [ ] 100% backward compatibility with existing demo

---

**Version:** 1.0.0
**Status:** READY TO IMPLEMENT
**Next:** Begin Phase 1 Implementation

