import { useCallback, useEffect, useState } from "react";
import {
  cancelExecution,
  continueExecution,
  createExecution,
  getExecution,
  getExecutionSteps,
  listDemoCases,
  validateDemoCase,
} from "../services/api";
import type { AuthState, DemoCase, Execution, ExecutionStep, ValidationResult } from "../types";
import { DataMappingPanel } from "../components/DataMappingPanel";
import { ExecutionConsole } from "../components/ExecutionConsole";
import { ExecutionResultPanel } from "../components/ExecutionResultPanel";
import { HumanActionDialog } from "../components/HumanActionDialog";
import { StatusBadge } from "../components/StatusBadge";
import { ValidationPanel } from "../components/ValidationPanel";
import { WorkflowStepList } from "../components/WorkflowStepList";
import { usePolling } from "../hooks/usePolling";

const TERMINAL = new Set(["COMPLETED", "FAILED", "CANCELLED"]);
const POLL_INTERVAL = 2000;

interface Props { auth: AuthState; onLogout: () => void; }

export function PMJayDemoPage({ auth, onLogout }: Props) {
  const [cases, setCases] = useState<DemoCase[]>([]);
  const [selectedCase, setSelectedCase] = useState<DemoCase | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [execution, setExecution] = useState<Execution | null>(null);
  const [steps, setSteps] = useState<ExecutionStep[]>([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<"workflow" | "mapping">("workflow");

  // Load demo cases on mount
  useEffect(() => {
    listDemoCases()
      .then(setCases)
      .catch((e) => setError(e.message));
  }, []);

  // Select a case and run validation
  async function selectCase(c: DemoCase) {
    setSelectedCase(c);
    setValidation(null);
    setExecution(null);
    setSteps([]);
    setError(null);
    try {
      const v = await validateDemoCase(c.id);
      setValidation(v);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Validation failed");
    }
  }

  // Start execution
  async function startDemo() {
    if (!selectedCase) return;
    setError(null);
    setActionLoading(true);
    try {
      const ex = await createExecution(selectedCase.id);
      setExecution(ex);
      setSteps(ex.steps);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to start");
    } finally {
      setActionLoading(false);
    }
  }

  // Poll for updates while running
  const pollActive = !!(execution && !TERMINAL.has(execution.status));
  const poll = useCallback(async () => {
    if (!execution) return;
    try {
      const [ex, st] = await Promise.all([
        getExecution(execution.id),
        getExecutionSteps(execution.id),
      ]);
      setExecution(ex);
      setSteps(st);
    } catch { /* silent */ }
  }, [execution]);
  usePolling(poll, POLL_INTERVAL, pollActive);

  // Human-in-the-loop: continue
  async function handleContinue(note: string) {
    if (!execution) return;
    setActionLoading(true);
    try {
      const ex = await continueExecution(execution.id, note);
      setExecution(ex);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Continue failed");
    } finally {
      setActionLoading(false);
    }
  }

  // Cancel
  async function handleCancel() {
    if (!execution) return;
    setActionLoading(true);
    try {
      const ex = await cancelExecution(execution.id);
      setExecution(ex);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Cancel failed");
    } finally {
      setActionLoading(false);
    }
  }

  const isTerminal = execution ? TERMINAL.has(execution.status) : false;
  const isWaiting = execution?.status === "WAITING_FOR_HUMAN";

  return (
    <div style={{ padding: "1.5rem", maxWidth: "1300px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <div>
          <h1 style={{ color: "#f1f5f9", fontSize: "1.3rem", margin: 0 }}>
            PM-JAY Beneficiary / Case Processing Demo
          </h1>
          <p style={{ color: "#475569", fontSize: "0.82rem", margin: "4px 0 0" }}>
            Authorized portal workflow demonstration · Signed in as <strong style={{ color: "#94a3b8" }}>{auth.email}</strong>
          </p>
        </div>
        <button onClick={onLogout} style={{ background: "transparent", color: "#64748b", border: "1px solid #334155", borderRadius: "6px", padding: "0.4rem 0.9rem", cursor: "pointer", fontSize: "0.85rem" }}>
          Sign out
        </button>
      </div>

      {error && (
        <div role="alert" style={{ background: "#450a0a", color: "#fca5a5", borderRadius: "6px", padding: "0.65rem 1rem", marginBottom: "1rem", fontSize: "0.85rem" }}>
          {error}
        </div>
      )}

      {/* Case selector */}
      <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "10px", padding: "1rem", marginBottom: "1.25rem" }}>
        <h2 style={{ color: "#94a3b8", fontSize: "0.8rem", letterSpacing: "0.06em", margin: "0 0 0.75rem" }}>
          SELECT DEMO CASE
        </h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          {cases.map((c) => (
            <button
              key={c.id}
              onClick={() => selectCase(c)}
              aria-pressed={selectedCase?.id === c.id}
              style={{
                background: selectedCase?.id === c.id ? "#1e3a5f" : "#0f172a",
                color: selectedCase?.id === c.id ? "#60a5fa" : "#94a3b8",
                border: `2px solid ${selectedCase?.id === c.id ? "#3b82f6" : "#334155"}`,
                borderRadius: "8px",
                padding: "0.6rem 1rem",
                cursor: "pointer",
                fontSize: "0.85rem",
                fontWeight: selectedCase?.id === c.id ? 700 : 400,
              }}
            >
              {c.case_ref}
              <div style={{ fontSize: "0.72rem", color: "#475569", fontWeight: 400 }}>{c.demo_patient_name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Selected case detail + start button */}
      {selectedCase && (
        <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "10px", padding: "1rem", marginBottom: "1.25rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <div style={{ display: "inline-block", background: "#b45309", color: "#fff", fontSize: "0.65rem", fontWeight: 700, padding: "2px 8px", borderRadius: "4px", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                SYNTHETIC DATA
              </div>
              <h3 style={{ color: "#f1f5f9", margin: "0 0 0.5rem", fontSize: "1.05rem" }}>{selectedCase.demo_patient_name}</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "0.4rem 1.5rem", fontSize: "0.82rem" }}>
                {[
                  ["Beneficiary ID", selectedCase.demo_beneficiary_id],
                  ["Date of Birth", selectedCase.demo_dob],
                  ["Gender", selectedCase.demo_gender],
                  ["Hospital", selectedCase.demo_hospital_name],
                  ["Procedure", selectedCase.demo_procedure_name],
                  ["Amount", `₹${Number(selectedCase.demo_amount).toLocaleString("en-IN")}`],
                ].map(([label, val]) => (
                  <div key={label}>
                    <span style={{ color: "#475569" }}>{label}: </span>
                    <span style={{ color: "#cbd5e1" }}>{val}</span>
                  </div>
                ))}
              </div>
            </div>
            <button
              onClick={startDemo}
              disabled={actionLoading || (!!execution && !isTerminal)}
              aria-label="Start live automation for selected demo case"
              style={{
                background: (actionLoading || (!!execution && !isTerminal)) ? "#334155" : "#3b82f6",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                padding: "0.75rem 1.5rem",
                fontWeight: 700,
                fontSize: "0.95rem",
                cursor: (actionLoading || (!!execution && !isTerminal)) ? "not-allowed" : "pointer",
                whiteSpace: "nowrap",
              }}
            >
              {actionLoading ? "Starting…" : execution && !isTerminal ? "Running…" : "▶ Start Live Automation"}
            </button>
          </div>

          {validation && (
            <div style={{ marginTop: "1rem" }}>
              <ValidationPanel checks={validation.checks} passed={validation.passed} />
            </div>
          )}
        </div>
      )}

      {/* Main execution area */}
      {execution && (
        <div>
          {/* Execution status bar */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
            <StatusBadge status={execution.status} />
            {execution.status === "RUNNING" && (
              <span style={{ color: "#60a5fa", fontSize: "0.82rem", animation: "pulse 1.5s infinite" }}>
                Browser automation running…
              </span>
            )}
            <span style={{ color: "#475569", fontSize: "0.78rem", fontFamily: "monospace" }}>
              ID: {execution.id.slice(0, 8)}…
            </span>
            {!isTerminal && (
              <button
                onClick={handleCancel}
                disabled={actionLoading}
                style={{ background: "transparent", color: "#f87171", border: "1px solid #f87171", borderRadius: "4px", padding: "0.25rem 0.75rem", fontSize: "0.8rem", cursor: actionLoading ? "not-allowed" : "pointer", marginLeft: "auto" }}
              >
                Cancel
              </button>
            )}
          </div>

          {/* WAITING_FOR_HUMAN dialog */}
          {isWaiting && execution.waiting_reason && (
            <HumanActionDialog
              reason={execution.waiting_reason}
              executionId={execution.id}
              onContinue={handleContinue}
              onCancel={handleCancel}
              loading={actionLoading}
            />
          )}

          {/* Tabs: Workflow | Mapping */}
          <div style={{ display: "flex", gap: "0", marginBottom: "1rem", borderBottom: "1px solid #334155" }}>
            {(["workflow", "mapping"] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                aria-selected={tab === t}
                style={{
                  background: "transparent",
                  color: tab === t ? "#60a5fa" : "#475569",
                  border: "none",
                  borderBottom: tab === t ? "2px solid #3b82f6" : "2px solid transparent",
                  padding: "0.6rem 1.25rem",
                  fontWeight: tab === t ? 700 : 400,
                  fontSize: "0.88rem",
                  cursor: "pointer",
                }}
              >
                {t === "workflow" ? "Workflow Execution" : "Field Mapping"}
              </button>
            ))}
          </div>

          {tab === "workflow" && (
            <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "1.25rem", alignItems: "start" }}>
              {/* Left: step list */}
              <div style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "10px", padding: "1rem" }}>
                <h3 style={{ color: "#94a3b8", fontSize: "0.78rem", letterSpacing: "0.06em", margin: "0 0 0.75rem" }}>
                  PM-JAY WORKFLOW
                </h3>
                <WorkflowStepList steps={steps} currentStep={execution.current_step} />
              </div>

              {/* Right: console */}
              <div>
                <h3 style={{ color: "#94a3b8", fontSize: "0.78rem", letterSpacing: "0.06em", margin: "0 0 0.5rem" }}>
                  EXECUTION CONSOLE
                </h3>
                <ExecutionConsole steps={steps} />
              </div>
            </div>
          )}

          {tab === "mapping" && selectedCase && (
            <DataMappingPanel demoCase={selectedCase} />
          )}

          {/* Result panel — terminal states */}
          {isTerminal && (
            <ExecutionResultPanel execution={execution} />
          )}
        </div>
      )}

      {/* Empty state */}
      {!selectedCase && cases.length > 0 && (
        <div style={{ textAlign: "center", padding: "3rem", color: "#334155" }}>
          <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>↑</div>
          <p>Select a demo case above to begin</p>
        </div>
      )}
    </div>
  );
}
