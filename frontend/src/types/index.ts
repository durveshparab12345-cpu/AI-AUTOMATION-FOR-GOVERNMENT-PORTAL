// =============================================================================
// AI Portal Automation Platform — Shared TypeScript types
// Stage 2A: PM-JAY Demo Prototype
// =============================================================================

export type ExecutionStatus =
  | "PENDING"
  | "RUNNING"
  | "WAITING_FOR_HUMAN"
  | "VALIDATING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export type StepStatus =
  | "PENDING"
  | "RUNNING"
  | "WAITING_FOR_HUMAN"
  | "SUCCESS"
  | "FAILED"
  | "SKIPPED";

export interface DemoCase {
  id: string;
  case_ref: string;
  demo_patient_name: string;
  demo_beneficiary_id: string;
  demo_dob: string;
  demo_gender: string;
  demo_hospital_name: string;
  demo_hospital_code: string;
  demo_procedure_name: string;
  demo_procedure_code: string;
  demo_amount: number;
  demo_documents: string; // JSON string
  demo_is_synthetic: boolean;
  is_active: boolean;
  created_at: string;
}

export interface ExecutionStep {
  id: string;
  step_number: number;
  step_name: string;
  status: StepStatus;
  message: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface Execution {
  id: string;
  organization_id: string;
  demo_case_id: string | null;
  workflow_name: string;
  initiated_by: string;
  status: ExecutionStatus;
  current_step: number;
  waiting_reason: string | null;
  error_message: string | null;
  portal_result: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  steps: ExecutionStep[];
}

export interface ValidationCheck {
  name: string;
  passed: boolean;
  message: string;
}

export interface ValidationResult {
  passed: boolean;
  checks: ValidationCheck[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  organization_id: string;
  user_email: string;
  user_name: string;
}

export interface AuthState {
  token: string | null;
  email: string | null;
  name: string | null;
  organizationId: string | null;
}

// Field mapping entry for the data mapping panel
export interface FieldMapping {
  internalLabel: string;
  internalValue: string;
  portalLabel: string;
}
