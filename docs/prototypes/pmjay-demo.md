# PM-JAY Demo Prototype

## Purpose

This prototype demonstrates the AI Portal Automation Platform concept using a
PM-JAY/TMS portal workflow. It shows how a teach-once, execute-repeatedly
automation system works — including human-in-the-loop control for every step
that requires security actions or sensitive submissions.

**This is a prototype, not a production system.**

---

## Authorized Use Requirement

This prototype MUST only be used with portal accounts and environments that
the operating organization is legally authorized to access.

It does NOT bypass CAPTCHA, OTP, DSC, MFA, or any portal security control.
Every such step pauses and displays "Human Action Required" for the operator
to complete manually.

---

## Demo Architecture

```
Browser (React UI)
   ↓ login / select case / start demo
FastAPI (backend)
   ↓ validate demo case
   ↓ create AutomationExecution record
   ↓ start background WorkflowRunner
WorkflowRunner
   ↓ step 1: validate synthetic data
   ↓ step 2: open browser (Playwright, visible)
   ↓ step 3: PAUSE → operator authenticates
   ↓ step 4: navigate to beneficiary section
   ↓ step 5: search for beneficiary
   ↓ step 6: read page content
   ↓ step 7: map fields
   ↓ step 8: PAUSE → human confirmation before submission
   ↓ step 9: capture portal result
   ↓ step 10: complete
PMJAYAdapter (portal-specific logic)
   ↓ uses BrowserSession (Playwright)
   ↓ raises HumanActionRequired for OTP/CAPTCHA/DSC
Authorized PM-JAY/TMS Portal
```

---

## Workflow Steps

| # | Step | Automated? |
|---|------|-----------|
| 1 | Initialize & validate demo data | Yes |
| 2 | Open PM-JAY portal in browser | Yes |
| 3 | Authenticate operator | **Human required** |
| 4 | Navigate to beneficiary section | Yes (falls back to human if element not found) |
| 5 | Search for beneficiary | Yes (falls back to human if element not found) |
| 6 | Read page information | Yes |
| 7 | Map case data to portal fields | Yes |
| 8 | Confirm before submission | **Always human required** |
| 9 | Capture portal result | Yes |
| 10 | Complete | Yes |

---

## Human-in-the-Loop Design

When `HumanActionRequired` is raised:
- Execution enters `WAITING_FOR_HUMAN` state
- UI shows the reason clearly
- Operator completes the required action (OTP, CAPTCHA, DSC, confirmation)
- Operator clicks **Continue** — workflow resumes from the paused step
- Operator can click **Stop Workflow** to cancel at any time

The system NEVER attempts to bypass security controls.

---

## Demo Cases (Synthetic Data Only)

Three synthetic demo cases are seeded on startup:

| Case | Patient | Procedure | Amount |
|------|---------|-----------|--------|
| DEMO-CASE-001 | SYNTHETIC PATIENT ALPHA | Appendectomy | ₹25,000 |
| DEMO-CASE-002 | SYNTHETIC PATIENT BETA | Cataract Surgery | ₹12,000 |
| DEMO-CASE-003 | SYNTHETIC PATIENT GAMMA | Maternity Package | ₹9,000 |

No real patient data. The `demo_is_synthetic = true` flag is enforced in code.

---

## How to Configure

1. Copy `.env.example` → `backend/.env`
2. Set `DATABASE_URL` to your PostgreSQL instance
3. Set `BROWSER_HEADLESS=false` for live visible demo
4. Set `DEMO_MODE=true` to auto-seed demo data
5. Run migrations: `alembic upgrade head`

---

## How to Run

```bash
# Backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

Navigate to http://localhost:5173

Login: `demo@ai-portal-demo.local` / `DemoPassword@2026`

---

## How to Test

```bash
cd backend
.venv\Scripts\pytest tests/ -v
```

31 tests — no real portal contacted, no real DB required (SQLite in-memory).

---

## Limitations

- Portal selectors in `PMJAYSelectors` are marked UNVERIFIED — confirmed only in authorized portal session
- Authentication is always handed to the operator — credentials are never stored
- Screenshot storage is local only — not served publicly
- No real claim submission is possible without operator confirmation
- Background tasks use PostgreSQL — SQLite tests mock the session factory

---

## What Requires an Authorized Real PM-JAY Environment

- Verifying portal CSS/ARIA selectors
- Confirming navigation paths after login
- Testing beneficiary search with real (authorized) data
- End-to-end execution past the authentication step
