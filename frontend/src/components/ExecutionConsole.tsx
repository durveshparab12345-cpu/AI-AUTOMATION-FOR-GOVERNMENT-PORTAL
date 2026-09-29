// Right-panel live execution console
import type { ExecutionStep } from "../types";

function formatTime(iso: string | null): string {
  if (!iso) return "--:--:--";
  return new Date(iso).toLocaleTimeString("en-IN", { hour12: false });
}

const ROW_COLOR: Record<string, string> = {
  SUCCESS: "#4ade80",
  FAILED: "#f87171",
  WAITING_FOR_HUMAN: "#fdba74",
  RUNNING: "#60a5fa",
  PENDING: "#475569",
  SKIPPED: "#64748b",
};

interface Props {
  steps: ExecutionStep[];
}

export function ExecutionConsole({ steps }: Props) {
  const active = steps.filter((s) => s.status !== "PENDING");

  return (
    <div
      role="log"
      aria-label="Execution console"
      aria-live="polite"
      style={{
        background: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: "8px",
        padding: "0.75rem",
        fontFamily: "monospace",
        fontSize: "0.8rem",
        minHeight: "200px",
        maxHeight: "320px",
        overflowY: "auto",
      }}
    >
      {/* Header row */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "80px 1fr 120px",
          gap: "0.5rem",
          color: "#475569",
          fontSize: "0.7rem",
          borderBottom: "1px solid #1e293b",
          paddingBottom: "0.4rem",
          marginBottom: "0.4rem",
          fontWeight: 700,
        }}
      >
        <span>TIME</span>
        <span>ACTION</span>
        <span>STATUS</span>
      </div>

      {active.length === 0 && (
        <div style={{ color: "#334155", padding: "0.5rem 0" }}>
          Waiting to start…
        </div>
      )}

      {active.map((step) => (
        <div
          key={step.id}
          style={{
            display: "grid",
            gridTemplateColumns: "80px 1fr 120px",
            gap: "0.5rem",
            padding: "3px 0",
            borderBottom: "1px solid #0f172a",
            alignItems: "start",
          }}
        >
          <span style={{ color: "#475569" }}>
            {formatTime(step.started_at)}
          </span>
          <span style={{ color: "#cbd5e1" }}>
            {step.step_name}
            {step.message && step.status !== "PENDING" && (
              <div style={{ color: "#64748b", fontSize: "0.72rem" }}>
                {step.message}
              </div>
            )}
          </span>
          <span
            style={{
              color: ROW_COLOR[step.status] ?? "#94a3b8",
              fontWeight: 700,
              fontSize: "0.72rem",
            }}
          >
            {step.status.replace(/_/g, " ")}
          </span>
        </div>
      ))}
    </div>
  );
}
