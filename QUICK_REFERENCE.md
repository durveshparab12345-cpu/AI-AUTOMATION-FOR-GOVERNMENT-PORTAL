# Quick Reference Card - Phase 1 Production Foundation

## ✅ System Status

```
🟢 OPERATIONAL

Backend:   http://localhost:8000 
Frontend:  http://localhost:5173
Database:  PostgreSQL connected
Migrations: Applied
```

## 🚀 Quick Start (30 seconds)

```bash
# Terminal 1: Backend
cd backend
.venv\Scripts\uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev

# Test: Health check
curl http://localhost:8000/api/v1/health
```

## 📊 Architecture Quick Facts

| Layer | Status | Examples |
|-------|--------|----------|
| Frontend | ✅ Running | React app at :5173 |
| API | ✅ 40% wired | /auth, /health, /pmjay_demo |
| Services | ✅ 95% complete | authorization, case, audit |
| Repositories | ✅ 100% complete | UserRepo, RoleRepo, CaseRepo |
| Models | ✅ 100% complete | User, Role, Case, Beneficiary, AuditLog |
| Database | ✅ 90% ready | Tables created, needs seed data |
| Tests | ⏳ 0% | Not yet written |
| Middleware | ⏳ 30% | TenantContext, RequestID, others |

## 🔑 Key Files

**Must Know:**
- `app/main.py` - Entry point (add middleware here)
- `app/models/base.py` - BaseModel with audit fields (id, tenant_id, audit fields)
- `app/models/user.py` - User model with RBAC methods
- `app/core/constants.py` - All enums (CaseStatus, RoleName, ActionType, etc)
- `app/services/` - Business logic (authorization, case, audit)
- `app/repositories/` - Data access (user, role, case, audit)

**Configuration:**
- `app/core/config.py` - 50+ settings, Environment enum
- `.env` - DATABASE_URL, JWT_SECRET, API_KEY
- `alembic.ini` - Migration config

**Database:**
- `alembic/versions/` - Migration files
- Tables: users, roles, permissions, cases, beneficiaries, audit_logs, organizations

## 🔐 Key Security Concepts

**Multi-Tenancy:**
- Every model has `tenant_id` (inherited from BaseModel)
- All queries filter by `tenant_id`
- `tenant_id` comes from JWT token

**RBAC:**
- User has many Roles
- Role has many Permissions
- Permission = Resource + Action (e.g., "CASE", "CREATE")
- Check: `user.has_permission("CASE", "CREATE")`

**Audit:**
- All mutations create AuditLog entry
- Immutable append-only (no updates)
- Tracks: user_id, request_id, IP, old/new values, timestamp

**Encryption:**
- Passwords: bcrypt
- Sensitive data: AES-256-GCM
- Tokens: JWT (signed, not encrypted by default)

## 📝 Common Tasks

### Add New API Endpoint

1. **Create route in** `app/api/v1/your_feature.py`
```python
@router.post("/your-endpoint")
async def your_endpoint(data: YourSchema, db: AsyncSession = Depends(get_db)):
    repo = YourRepository(db)
    result = await repo.create(data)
    return result
```

2. **Include router in** `app/main.py`
```python
from app.api.v1 import your_feature as your_router
# In create_app()
app.include_router(your_router.router, prefix="/api/v1")
```

3. **Create schema in** `app/schemas/your_feature.py`
```python
from pydantic import BaseModel

class YourSchema(BaseModel):
    field_name: str
    
class YourResponse(BaseModel):
    id: UUID
    field_name: str
```

### Add Permission Check

```python
from app.utils.decorators import require_permission

@router.post("/cases")
@require_permission("CASE", "CREATE")
async def create_case(data: CaseSchema, current_user: User = Depends(get_current_user)):
    # User must have CASE:CREATE permission
    ...
```

### Log Audit Event

```python
from app.services.audit_service import AuditService
from app.core.constants import ActionType

audit_service = AuditService(db)
await audit_service.log_action(
    user_id=current_user.id,
    resource_type="CASE",
    action_type=ActionType.CREATE,
    resource_id=case.id,
    old_values=None,
    new_values=case.dict()
)
```

### Create User Repository Query

```python
# In app/repositories/user_repository.py
async def get_by_email_and_org(self, email: str, org_id: UUID):
    result = await self.session.execute(
        select(User).where(
            and_(
                User.email == email,
                User.tenant_id == org_id,
                User.is_active == True
            )
        )
    )
    return result.scalar_one_or_none()
```

## 🧪 Testing Quick Commands

```bash
# Run all tests
cd backend && pytest

# Run specific test
pytest app/tests/test_auth.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test class
pytest app/tests/test_auth.py::TestLogin

# Run in verbose mode
pytest -v
```

## 🐛 Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "no property 'organization'" | Using old field names | Use `tenant_id` not `organization_id` |
| "Mapper has no property" | Migration schema mismatch | Run migrations: `alembic upgrade head` |
| "Cannot transition from X to Y" | Invalid state transition | Check `CASE_STATE_TRANSITIONS` in constants |
| "Cross-tenant access" | Missing tenant_id filter | Add `.where(Model.tenant_id == tenant_id)` |
| "401 Unauthorized" | Invalid JWT | Check JWT_SECRET in .env |
| "403 Forbidden" | Missing permission | Check `has_permission()` logic |

## 🎯 Immediate Next Steps

1. **30 min:** Wire remaining endpoints (roles, cases, audit)
2. **1 hour:** Integrate middleware into main.py
3. **1 hour:** Write critical tests (multi-tenant, RBAC)
4. **30 min:** Fix demo data seeding
5. **30 min:** Verification and integration testing

## 📚 Database Schema Reference

```
users (tenant_id → organizations)
├── id: UUID
├── tenant_id: UUID → organizations
├── email: String (unique)
├── first_name, last_name: String
├── hashed_password: String
├── is_active: Boolean
├── created_at, updated_at: DateTime
└── created_by, updated_by: UUID → users

organizations
├── id: UUID
├── name: String
├── slug: String
└── created_at: DateTime

roles (tenant_id → organizations)
├── id: UUID
├── tenant_id: UUID
├── name: String
├── is_system: Boolean
└── permissions: [Permission] (M2M)

permissions
├── id: UUID
├── resource: String
├── action: String
└── (resource, action) unique

user_roles
├── user_id → users
├── role_id → roles
├── assigned_at: DateTime
└── revoked_at: DateTime

cases (tenant_id → organizations)
├── id: UUID
├── tenant_id: UUID
├── case_number: String (unique)
├── status: Enum (14-state machine)
├── priority: Enum
├── beneficiary_id → beneficiaries
└── created_at, updated_at: DateTime

beneficiaries (tenant_id → organizations)
├── id: UUID
├── tenant_id: UUID
├── first_name, last_name: String
├── aadhar: String
├── date_of_birth: Date
└── eligibility_status: String

audit_logs (tenant_id → organizations)
├── id: UUID
├── tenant_id: UUID
├── user_id → users
├── resource_type: String
├── action: String
├── resource_id: UUID
├── old_values: JSON
├── new_values: JSON
└── created_at: DateTime
```

## 🔗 Key Enums

**CaseStatus** (14 states):
```python
INITIATED → ADMISSION_VERIFIED → PREAUTH_SUBMITTED → PREAUTH_APPROVED
→ TREATMENT_STARTED → TREATMENT_IN_PROGRESS → TREATMENT_COMPLETED
→ DISCHARGE_INITIATED → DISCHARGE_COMPLETED → CLAIM_SUBMITTED
→ CLAIM_APPROVED → CLOSED (or CANCELLED/REJECTED)
```

**RoleName**:
- SUPER_ADMIN, ADMIN, MANAGER, OPERATOR, VIEWER, PMAM, MEDCO, etc.

**ActionType**:
- CREATE, READ, UPDATE, DELETE, EXECUTE, MANAGE, APPROVE, REJECT

**ResourceType**:
- USER, CASE, WORKFLOW, DOCUMENT, ROLE, PERMISSION, AUDIT

## 💾 ENV Variables Reference

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEMO_MODE=True
DEBUG=True
APP_ENV=development
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

## 🚨 Production Checklist

- [ ] Set DEBUG=False
- [ ] Set APP_ENV=production
- [ ] Use strong JWT_SECRET_KEY (32+ chars)
- [ ] Enable HTTPS only
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up proper logging (not stdout)
- [ ] Enable rate limiting
- [ ] Run database backups
- [ ] Set up monitoring/alerting
- [ ] Use managed PostgreSQL (not local)
- [ ] Configure secrets vault
- [ ] Set up CI/CD pipeline

---

**Last Updated:** Session 2026-09-30  
**Next Review:** When wiring remaining endpoints  
**Status:** 🟢 OPERATIONAL
