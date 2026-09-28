# Security Principles

This document describes the security principles that govern all stages of the
AI Portal Automation Platform. These principles are non-negotiable and must be
upheld in every feature and every stage of development.

---

## 1. No Hard-Coded Credentials

Passwords, API keys, database passwords, portal credentials, OTP seeds, DSC
pins, and all other secrets **must never appear in source code or committed
files**.

All secrets are managed exclusively via environment variables. The `.env` file
(which holds real values) is git-ignored and must never be committed.

The `.env.example` file contains only placeholder values and serves as a
documented reference — never as a source of real secrets.

---

## 2. Environment-Based Configuration

The application reads all sensitive configuration from environment variables at
startup via `app/core/config.py`. If a required secret is missing in a
non-development environment, the application fails fast with a clear error
rather than silently using an unsafe default.

---

## 3. Future: Encrypted Credential Storage

Portal credentials (usernames, passwords, digital signatures) will eventually
be stored in an encrypted credential vault — never in plain text in the
database. The vault design will be implemented in a future stage with:

- Encryption at rest (AES-256 or equivalent)
- Key management separate from the application database
- Audit logging for every credential access
- Role-based access control on credential retrieval

---

## 4. Role-Based Access Control (RBAC)

The platform will support multiple roles per company:

- **Admin**: full access to portal configuration and user management
- **Operator**: can initiate and monitor workflow executions
- **Reviewer**: can approve or reject exceptions; read-only on other data
- **Auditor**: read-only access to audit logs

RBAC will be implemented in Stage 2 when authentication is introduced.

---

## 5. Audit Logging

Every significant action is recorded in an immutable audit log:

- User authentication events
- Workflow execution starts, completions, and failures
- Portal interactions (with masked sensitive fields)
- Approval and rejection decisions
- Credential access events
- Configuration changes

Audit logs are append-only and must not be deletable by application users.

---

## 6. Human Approval for Sensitive Actions

Certain portal actions (e.g., submitting a claim, approving a payment,
modifying patient records) require explicit human approval before execution.

The system will never allow the AI or the automation engine to take these
actions autonomously. The approval gate is enforced at the Workflow Engine
level — not just at the UI level.

---

## 7. Authorized Portal Access Only

The platform is designed to automate workflows that the business is already
authorized to perform. It must never:

- Access portals for which the company has no authorization
- Impersonate users who have not granted consent
- Operate outside the scope of the defined workflow

Authorization proofs (e.g., government authorization letters, portal access
agreements) are the responsibility of the deploying organization.

---

## 8. No CAPTCHA/OTP/DSC Bypassing

The platform must not implement any mechanism intended to defeat portal
security controls, including:

- CAPTCHA solving (automated or third-party)
- OTP interception or bypass
- DSC (Digital Signature Certificate) forgery or unauthorized use
- Session hijacking

If a portal requires CAPTCHA, OTP, or DSC authentication, those steps must be
handled by a legitimate human user. The platform may pause and prompt the
operator, but it must not attempt to circumvent these controls.

---

## 9. No Real Patient or Sensitive Data During Development

Development and testing environments must use synthetic, anonymized test data
only. Real patient names, identification numbers, claim data, or any other
personally identifiable information (PII) must never appear in:

- Source code
- Test fixtures
- Log files
- Development databases
- Screenshots or documentation

---

## 10. Input Validation

All data entering the system — from users, from portals, from AI suggestions —
is validated at the API boundary using Pydantic schemas before it reaches the
service or repository layers. No raw, unvalidated input reaches the database.
