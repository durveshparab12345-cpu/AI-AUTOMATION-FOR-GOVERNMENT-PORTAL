# Workflows

## What Is a Workflow?

In the AI Portal Automation Platform, a **workflow** is a structured,
versioned definition of a repeatable business process that involves interacting
with a portal.

Workflows are **data, not code**. They are stored in the database and can be
created, reviewed, versioned, and updated by authorized users — without
modifying or redeploying the application.

---

## Why Structured Data Instead of Hard-Coded Scripts?

Hard-coding automation as scripts creates several problems:

1. **No auditability** — you cannot easily review what a script will do before running it.
2. **No versioning** — rolling back a change requires a code deployment.
3. **No multi-tenancy** — each company would need its own script variant.
4. **No human-in-the-loop** — a script either runs fully or not at all.
5. **No AI integration** — a script cannot easily incorporate AI-suggested values.

Structured workflow definitions solve all of these.

---

## Planned Workflow Data Model

A workflow definition will contain:

```
Workflow
├── id
├── name
├── portal_id            → which portal this workflow operates on
├── company_id           → tenant-scoped
├── current_version_id   → pointer to the active version
└── versions[]
    └── WorkflowVersion
        ├── version_number
        ├── status           (draft | active | deprecated)
        ├── steps[]
        │   └── WorkflowStep
        │       ├── step_number
        │       ├── action_type  (navigate | click | fill | select | submit | wait | capture)
        │       ├── selector     (CSS or XPath selector for the target element)
        │       ├── field_mapping_id  → resolves the data value at runtime
        │       └── validation_rules[]
        └── created_at
```

---

## Workflow Execution

When a workflow is executed:

1. The **Workflow Engine** loads the active version of the workflow definition.
2. For each step, it resolves the required data via **field mappings** and **company rules**.
3. If AI assistance is enabled, the **AI Reasoning Layer** may suggest corrections or fill in ambiguous fields.
4. The **Validation Engine** confirms the resolved values meet all constraints.
5. If the step is flagged as sensitive, a **Human Approval Gate** pauses execution.
6. Once approved, the **Browser Automation Layer** (Playwright) executes the step.
7. Every step result is written to the **Execution Log**.

---

## Company Rules and Field Mappings

Each company may have custom rules that override default workflow behavior:

- **Company Rules**: conditions that must be met before a step executes (e.g., "only submit if claim value < ₹50,000").
- **Field Mappings**: mappings from internal data fields to portal form fields (e.g., `patient.aadhaar_number` → `#patient-id-input`).

These are stored per company per workflow version, allowing multiple companies to share the same base workflow while maintaining their own configuration.

---

## What Is NOT a Workflow

- A workflow is not a Python script.
- A workflow is not a Playwright test suite.
- A workflow is not an AI prompt.
- A workflow is not a hard-coded sequence of API calls.

All of those may be used *by* the workflow execution engine internally, but the workflow definition itself is always structured, reviewable, and versioned data.

---

## Current Status: Stage 1

No workflows are implemented yet. The data model, workflow engine, and execution infrastructure will be introduced in future stages.
