// =============================================================================
// API client service
// All backend communication goes through this module.
// =============================================================================

import type {
  DemoCase,
  Execution,
  ExecutionStep,
  TokenResponse,
  ValidationResult,
} from "../types";

const BASE_URL = "/api/v1";

// ---------------------------------------------------------------------------
// Auth storage helpers — token stored in memory only (not localStorage)
// to reduce XSS exposure risk for this prototype.
// ---------------------------------------------------------------------------
let _token: string | null = null;

export function setToken(token: string): void {
  _token = token;
}

export function clearToken(): void {
  _token = null;
}

export function getToken(): string | null {
  return _token;
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------
async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (_token) {
    headers["Authorization"] = `Bearer ${_token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorBody?.detail ?? `HTTP ${response.status}`
    );
  }

  return response.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------
export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  // OAuth2 password flow requires form-encoded body
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    body,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new ApiError(response.status, err?.detail ?? "Login failed");
  }

  return response.json() as Promise<TokenResponse>;
}

// ---------------------------------------------------------------------------
// Demo cases
// ---------------------------------------------------------------------------
export async function listDemoCases(): Promise<DemoCase[]> {
  return apiFetch<DemoCase[]>("/pmjay-demo/cases");
}

export async function validateDemoCase(
  caseId: string
): Promise<ValidationResult> {
  return apiFetch<ValidationResult>(`/pmjay-demo/cases/${caseId}/validate`);
}

// ---------------------------------------------------------------------------
// Executions
// ---------------------------------------------------------------------------
export async function createExecution(
  demoCaseId: string,
  workflowName?: string
): Promise<Execution> {
  return apiFetch<Execution>("/pmjay-demo/executions", {
    method: "POST",
    body: JSON.stringify({
      demo_case_id: demoCaseId,
      workflow_name:
        workflowName ?? "PM-JAY Beneficiary / Case Processing Demo",
    }),
  });
}

export async function listExecutions(): Promise<Execution[]> {
  return apiFetch<Execution[]>("/pmjay-demo/executions");
}

export async function getExecution(executionId: string): Promise<Execution> {
  return apiFetch<Execution>(`/pmjay-demo/executions/${executionId}`);
}

export async function getExecutionSteps(
  executionId: string
): Promise<ExecutionStep[]> {
  return apiFetch<ExecutionStep[]>(
    `/pmjay-demo/executions/${executionId}/steps`
  );
}

export async function continueExecution(
  executionId: string,
  operatorNote?: string
): Promise<Execution> {
  return apiFetch<Execution>(
    `/pmjay-demo/executions/${executionId}/continue`,
    {
      method: "POST",
      body: JSON.stringify({ operator_note: operatorNote ?? null }),
    }
  );
}

export async function cancelExecution(
  executionId: string
): Promise<Execution> {
  return apiFetch<Execution>(
    `/pmjay-demo/executions/${executionId}/cancel`,
    { method: "POST", body: JSON.stringify({}) }
  );
}
