# Architecture Overview — Stage 2A

## Updated System Architecture

```
User (Authorized Operator)
        │
        ▼
┌─────────────────────────────┐
│   Frontend (React + Vite)   │
│   - Login                   │
│   - Demo case selection     │
│   - Live execution dashboard│
│   - Human action dialog     │
└────────────┬────────────────┘
             │ HTTPS / REST + polling
             ▼
┌─────────────────────────────┐
│   FastAPI (Backend API)     │
│   - JWT authentication      │
│   - Organization isolation  │
│   - /api/v1/auth            │
│   - /api/v1/pmjay-demo      │
│   - /api/v1/health          │
└────────────┬────────────────┘
             │ background task
             ▼
┌─────────────────────────────┐
│   WorkflowRunner            │
│   - Step orchestration      │
│   - State machine           │
│   - Execution logging       │
└─────┬──────────┬────────────┘
      │          │
      ▼          ▼
┌──────────┐ ┌──────────────────────┐
│Validation│ │  PMJAYAdapter        │
│Service   │ │  (portal-specific)   │
│(determin-│ │  - connect()         │
│istic,    │ │  - authenticate()    │
│no LLM)   │ │  - navigate()        │
└──────────┘ │  - search()          │
             │  - read_page()       │
             │  - fill_field()      │
             │  - request_human()   │
             └──────────┬───────────┘
                         │
                         ▓ HumanActionRequired raised here
                         │ for OTP / CAPTCHA / DSC / confirmation
                         ▼
              ┌──────────────────────┐
              │  BrowserSession      │
              │  (Playwright)        │
              │  - visible browser   │
              │  - role/text/label   │
              │    selectors only    │
              │  - screenshot capture│
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Authorized PM-JAY   │
              │  / TMS Portal        │
              └──────────────────────┘
```

## Execution Audit Path

```
AutomationExecution (DB record)
   └── AutomationExecutionStep × N (DB records)
       - step_name, status, message, timestamps
       - NO credentials, NO tokens stored
```

## AI Control Principle

The AI reasoning layer is NOT connected in Stage 2A.
All decisions are deterministic (ValidationService) or
deferred to the human operator.

AI will be added in a future stage — it will ADVISE,
never autonomously control critical portal actions.

## Security Boundary

```
NEVER automated:                    ALWAYS human:
- Portal credentials                - Login step
- OTP / CAPTCHA / DSC               - Any OTP prompt
- Sensitive submission              - Pre-submission confirmation
- Real patient data                 - All patient lookups
```
