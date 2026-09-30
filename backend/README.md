# AI Portal Automation Platform - Backend

Production-grade backend for the AI Portal Automation Platform, built with FastAPI, SQLAlchemy, and Celery.

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Pipenv or venv

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Initialize database
alembic upgrade head

# Seed demo data (optional)
python scripts/seed_demo_data.py
```

### Running the Application

```bash
# Start main API server
uvicorn app.main:app --reload

# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.workers.celery_app beat --loglevel=info
```

API will be available at `http://localhost:8000`

## Directory Structure

```
backend/
├── app/
│   ├── core/              # Core configuration and middleware
│   ├── api/               # API endpoints (v1, v2)
│   ├── models/            # Database models (SQLAlchemy)
│   ├── schemas/           # Request/response schemas (Pydantic)
│   ├── services/          # Business logic
│   ├── repositories/      # Data access layer
│   ├── utils/             # Utilities and helpers
│   ├── workers/           # Celery tasks
│   ├── tests/             # Test suite
│   ├── main.py            # FastAPI app entry point
│   ├── lifespan.py        # App startup/shutdown
│   └── exceptions.py      # Custom exceptions
├── config/                # Environment configurations
├── migrations/            # Database migrations (Alembic)
├── scripts/               # Utility scripts
├── docker/                # Docker configurations
├── docs/                  # Documentation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini             # Pytest configuration
└── README.md              # This file
```

## Architecture

See `docs/ARCHITECTURE.md` for comprehensive architecture documentation including:

- System overview and module relationships
- Multi-tenant architecture
- RBAC and authorization flow
- Case lifecycle and state machine
- Workflow engine architecture
- Execution engine architecture
- Database schema overview
- API versioning strategy
- Error handling and exceptions
- Audit and logging architecture

## Core Concepts

### Multi-Tenancy

The platform is designed as a true multi-tenant SaaS:

- All tables have `tenant_id` column for data isolation
- Queries automatically filtered by tenant
- TenantContextMiddleware extracts and validates tenant from JWT
- Supports complete data isolation at database level

### RBAC (Role-Based Access Control)

- Users have multiple roles (ADMIN, MANAGER, OPERATOR, VIEWER, etc.)
- Roles have permissions for specific resources and actions
- Example: `CASE:READ`, `CASE:CREATE`, `WORKFLOW:EXECUTE`
- Permissions checked via decorators and service methods

### Case Lifecycle

Cases progress through states:
```
INITIATED → ADMISSION_VERIFIED → PREAUTH_SUBMITTED → PREAUTH_APPROVED 
→ TREATMENT_STARTED → TREATMENT_IN_PROGRESS → TREATMENT_COMPLETED 
→ DISCHARGE_INITIATED → DISCHARGE_COMPLETED → CLAIM_SUBMITTED 
→ CLAIM_APPROVED → CLOSED
```

### Workflows

Automated workflows orchestrate case processing:

- AUTOMATION: Execute programmatic actions
- DECISION: Branch based on conditions
- NOTIFICATION: Send emails/messages
- HUMAN_INTERVENTION: Pause for manual action

### Data Security

- Passwords: bcrypt hashing with salt
- Sensitive data: AES-256-GCM encryption
- Credentials: Encrypted at rest, decrypted on demand
- Audit trail: Immutable logs of all changes

## API Endpoints

### v1 API

#### Authentication

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

#### Cases

- `POST /api/v1/cases` - Create case
- `GET /api/v1/cases` - List cases
- `GET /api/v1/cases/{case_id}` - Get case
- `PUT /api/v1/cases/{case_id}` - Update case
- `DELETE /api/v1/cases/{case_id}` - Delete case
- `GET /api/v1/cases/{case_id}/timeline` - Get case timeline

#### Other Resources

- `/api/v1/beneficiaries` - Beneficiary management
- `/api/v1/preauth` - Pre-authorization management
- `/api/v1/treatments` - Treatment records
- `/api/v1/discharges` - Discharge management
- `/api/v1/claims` - Claim processing
- `/api/v1/documents` - Document management
- `/api/v1/workflows` - Workflow management
- `/api/v1/executions` - Workflow execution
- `/api/v1/users` - User management
- `/api/v1/roles` - Role management
- `/api/v1/organizations` - Organization management
- `/api/v1/audit` - Audit logs

### Response Format

All responses follow consistent format:

**Success Response:**
```json
{
    "success": true,
    "data": {...},
    "metadata": {
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:30:00Z",
        "request_id": "req-123456"
    }
}
```

**Error Response:**
```json
{
    "success": false,
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

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_portal

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=noreply@aiportal.com
EMAIL_USERNAME=...
EMAIL_PASSWORD=...

# AWS S3 (for file storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=ai-portal-documents
AWS_REGION=us-east-1

# Application
APP_ENV=development  # or production, staging
DEBUG=true
LOG_LEVEL=DEBUG
```

### Configuration Files

Environment-specific YAML configs in `config/`:

- `development.yaml` - Development environment
- `staging.yaml` - Staging environment
- `production.yaml` - Production environment
- `test.yaml` - Test environment

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/unit/services/test_auth_service.py

# Run with markers
pytest -m "not integration"  # Skip integration tests
pytest -m "security"  # Run security tests only
```

### Test Organization

```
tests/
├── unit/              # Unit tests (fast, mocked)
├── integration/       # Integration tests (real database)
├── security/          # Security tests
├── e2e/               # End-to-end tests
├── fixtures/          # Test fixtures and data
└── conftest.py        # Pytest configuration
```

### Critical Test Areas

- Multi-tenant isolation
- RBAC enforcement
- Case state transitions
- Workflow execution
- Audit logging
- Data encryption

## Database Migrations

### Creating Migrations

```bash
# Create new migration
alembic revision -m "Description of change"

# Edit the generated file in alembic/versions/
```

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade 2dd10dd617f3

# Downgrade one version
alembic downgrade -1
```

## Development Workflow

### Project Setup

```bash
# Clone repository
git clone <repo-url>
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Linting
ruff check app/

# Type checking
mypy app/

# Format code
black app/

# All checks
make lint
```

### Commits

```bash
# Branches: feature/*, bugfix/*, hotfix/*, docs/*
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push -u origin feature/new-feature

# Create pull request
```

## Deployment

### Docker

```bash
# Build image
docker build -f docker/Dockerfile -t ai-portal:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  ai-portal:latest

# Docker Compose
docker-compose up -d
```

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] Redis connection verified
- [ ] AI provider credentials configured
- [ ] Email service configured
- [ ] S3 storage configured
- [ ] SSL certificates installed
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Monitoring/alerting setup
- [ ] Backup strategy implemented
- [ ] Load balancer configured

## Monitoring and Logging

### Logging

Structured logging with request IDs:

```python
logger.info(
    "Case created",
    extra={
        "request_id": request_id,
        "tenant_id": tenant_id,
        "case_id": case_id,
        "action": "CREATE",
    }
)
```

Logs location: `logs/` directory

### Audit Trail

All changes logged to `audit_logs` table:

- User who made change
- Resource that was changed
- Old and new values
- Timestamp
- Request ID for tracing

## Troubleshooting

### Common Issues

**Database Connection Error**
```
Check DATABASE_URL environment variable
Verify PostgreSQL is running
Check firewall/network settings
```

**Redis Connection Error**
```
Check REDIS_URL environment variable
Verify Redis is running
Check port 6379 is accessible
```

**JWT Token Errors**
```
Verify JWT_SECRET_KEY is set
Check token expiration
Verify Authorization header format: "Bearer <token>"
```

**Workflow Execution Failures**
```
Check Celery worker is running
Review execution logs in database
Check workflow step configuration
Verify required context variables available
```

## Performance Tips

- Use database indexes on frequently queried fields
- Enable Redis caching for repetitive queries
- Batch operations where possible
- Use async operations for I/O
- Monitor slow queries with database logs
- Profile CPU-intensive operations

## Security Best Practices

- Always use HTTPS in production
- Rotate JWT secrets regularly
- Use strong passwords for all accounts
- Encrypt sensitive data at rest
- Implement rate limiting
- Validate all inputs
- Use parameterized queries (handled by SQLAlchemy)
- Keep dependencies updated
- Monitor audit logs for suspicious activity
- Implement proper CORS policy

## Support and Documentation

- Architecture: `docs/ARCHITECTURE.md`
- API Documentation: Swagger UI at `/docs`
- Database Schema: See models in `app/models/`
- Example workflows: See `scripts/seed_demo_data.py`

## License

[Your License Here]

## Contributing

1. Create feature branch from `develop`
2. Make changes with tests
3. Run linting and type checking
4. Submit pull request to `develop`
5. After review, merge to `main` for release

---

**Version:** 1.0.0  
**Last Updated:** 2024-01-15  
**Status:** Production Ready
