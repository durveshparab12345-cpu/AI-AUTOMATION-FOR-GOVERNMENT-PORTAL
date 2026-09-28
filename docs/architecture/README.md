# Architecture Overview

## High-Level System Architecture

```
User (Authorized Business User)
        │
        ▼
┌─────────────────────────────┐
│   Frontend (React + Vite)   │
│   - Workflow management UI  │
│   - Execution monitoring    │
│   - Approval interface      │
└────────────┬────────────────┘
             │ HTTPS / REST
             ▼
┌─────────────────────────────┐
│   FastAPI (Backend API)     │
│   - Authentication          │
│   - Tenant isolation        │
│   - Request validation      │
│   - Audit logging           │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Workflow Engine           │
│   - Structured workflow     │
│     definitions (versioned) │
│   - Step orchestration      │
│   - State machine           │
└─────┬──────────┬────────────┘
      │          │
      ▼          ▼
┌──────────┐ ┌──────────────────────┐
│ AI       │ │ Validation Engine    │
│ Reasoning│ │ - Field mapping      │
│ Layer    │ │ - Business rules     │
│ (LLM)    │ │ - Data format checks │
└──────────┘ └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Human Approval Gate  │
              │ - Sensitive action   │
              │   review             │
              │ - Exception handling │
              └──────────┬───────────┘
                         │ (after approval)
                         ▼
              ┌──────────────────────┐
              │ Browser Automation   │
              │ (Playwright)         │
              │ - Controlled actions │
              │ - Screenshot capture │
              │ - Error detection    │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Target Portal        │
              │ (Government /        │
              │  Business Portal)    │
              └──────────────────────┘
```

---

## Architectural Principles

### 1. AI Must Not Have Unrestricted Control

The AI reasoning layer interprets workflow steps and suggests field values, but it **cannot directly trigger portal actions**. Every AI-suggested action must pass through:

1. The Validation Engine (business rules, field constraints)
2. The Human Approval Gate (for sensitive or irreversible actions)
3. The Workflow Engine's state checks (correct step sequence)

The AI is an advisor, not an actor.

### 2. Strict Layer Separation

Each layer has a single responsibility:

| Layer | Responsibility | May Call |
|---|---|---|
| API Routes | Request/response handling | Services only |
| Services | Business logic | Repositories, external APIs |
| Repositories | Data access | Database only |
| Workflow Engine | Step orchestration | Validation, AI, Browser Automation |
| Browser Automation | Portal interaction | Portal only |

No layer may skip levels or call upward.

### 3. Multi-Tenant Isolation

All data is scoped to a tenant (company). No query ever returns data across tenant boundaries. Tenant isolation is enforced at the repository layer, not just the route layer.

### 4. Versioned Workflows

Workflows are structured data, not code. A workflow has:
- A definition (steps, expected inputs/outputs, field mappings)
- A version history
- Company-specific rule overrides

This means workflows can be reviewed, rolled back, and audited without modifying application code.

### 5. Complete Audit Trail

Every significant action — especially portal interactions — is logged with:
- Who initiated it (user + company)
- What was attempted
- What the portal responded
- Whether human approval was obtained
- Timestamps and correlation IDs

---

## Current Stage: Stage 1

Stage 1 establishes only the API foundation and database connection layer. None of the workflow engine, AI layer, browser automation, or portal connectivity is implemented yet.
