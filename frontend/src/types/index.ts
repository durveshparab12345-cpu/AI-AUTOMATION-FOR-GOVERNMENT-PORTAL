// =============================================================================
// AI Portal Automation Platform — Shared TypeScript types
// Stage 2A: PM-JAY Live Prototype with Full Portal Management
// =============================================================================

// ===== Execution & Automation Types =====
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

export type CaseStatus =
  | "INITIATED"
  | "IN_PROGRESS"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "PROCESSING"
  | "COMPLETED"
  | "REJECTED"
  | "CANCELLED";

export type WorkflowStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";
export type PortalStatus = "ACTIVE" | "INACTIVE" | "MAINTENANCE";
export type UserRole = "ADMIN" | "OPERATOR" | "SUPERVISOR" | "VIEWER";

// ===== Demo Case Types =====
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

// ===== Portal Types =====
export interface Portal {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  url: string;
  status: PortalStatus;
  automation_config: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface CreatePortalInput {
  name: string;
  description: string;
  url: string;
  automation_config?: Record<string, unknown>;
}

// ===== Workflow Types =====
export interface WorkflowStep {
  id: string;
  name: string;
  description: string;
  order: number;
  action_type: string;
  configuration: Record<string, unknown>;
}

export interface Workflow {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  version: number;
  status: WorkflowStatus;
  steps: WorkflowStep[];
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface CreateWorkflowInput {
  name: string;
  description: string;
  steps: Array<{
    name: string;
    description: string;
    action_type: string;
    configuration: Record<string, unknown>;
  }>;
}

// ===== Case Types =====
export interface Beneficiary {
  id: string;
  name: string;
  email: string;
  phone: string;
  date_of_birth: string;
}

export interface Case {
  id: string;
  organization_id: string;
  case_number: string;
  beneficiary_id: string;
  beneficiary: Beneficiary;
  status: CaseStatus;
  description: string;
  estimated_amount: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  case_history: CaseHistoryEntry[];
}

export interface CaseHistoryEntry {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  details: string;
}

export interface CreateCaseInput {
  beneficiary_id: string;
  description: string;
  estimated_amount: number;
}

// ===== Automation & Execution Types =====
export interface AutomationInstance {
  id: string;
  organization_id: string;
  case_id: string;
  workflow_id: string;
  status: ExecutionStatus;
  progress: number; // 0-100
  current_step: number;
  total_steps: number;
  started_at: string | null;
  completed_at: string | null;
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

// ===== User & Organization Types =====
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  organization_id: string;
  is_active: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  name: string;
  permissions: string[];
  organization_id: string;
}

// ===== Audit & Report Types =====
export interface AuditLogEntry {
  id: string;
  user_id: string;
  user_email: string;
  action: string;
  resource_type: string;
  resource_id: string;
  changes: Record<string, unknown>;
  timestamp: string;
}

export interface Report {
  id: string;
  organization_id: string;
  name: string;
  type: string;
  generated_at: string;
  data: Record<string, unknown>;
}

// ===== Validation & Response Types =====
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

// ===== Pagination & List Response Types =====
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ===== UI/Form Helper Types =====
export interface FieldMapping {
  internalLabel: string;
  internalValue: string;
  portalLabel: string;
}

export interface FormError {
  field: string;
  message: string;
}

export interface ApiResponse<T = unknown> {
  data?: T;
  error?: string;
  success: boolean;
}
