// Final execution result panel — shown when execution reaches a terminal state
import type { Execution } from "../types";
import { StatusBadge } from "./StatusBadge";

interface Props {
  execution: Execution;
}

export function ExecutionResultPanel({ execution }: Props) {
  const totalSteps = execution.steps.length;
  const successCount = execution.steps.filter((s) => s.status === "SUCCESS").length;
  const waitingCount = execution.steps.filter((s) => s.status === "WAITING_FOR_HUMAN").length;
  const failedCount = execution.steps.filter((s) => s.status === "FAILED").length;

  let portalResult: Record<string, unknown> | null = null;
  if (execution.portal_result) {
    try {
      portalResult = JSON.parse(execution.portal_result);
    } catch {
      // ignore
    }
  }

  return (
    <div
      style={{
        background: "#1e293b",
        border: "1px solid #334155",
        borderRadius: "10px",
        padding: "1.25rem",
        marginTop: "1rem",
      }}
    >
      <h3
        style={{
          color: "#f1f5f9",
          margin: "0 0 1rem",
          fontSize: "1rem",
          letterSpacing: "0.04em",
        }}
      >
        PM-JAY DEMO EXECUTION REPORT
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "auto 1fr",
          gap: "0.4rem 1rem",
          fontSize: "0.85rem",
          marginBottom: "1rem",
        }}
      >
        <span style={{ color: "#64748b" }}>Status:</span>
        <StatusBadge status={execution.status} />

        <span style={{ color: "#64748b" }}>Execution ID:</span>
        <span style={{ color: "#94a3b8", fontFamily: "monospace", fontSize: "0.78rem" }}>
          {execution.id}
        </span>

        <span style={{ color: "#64748b" }}>Started:</span>
        <span style={{ color: "#94a3b8" }}>
          {execution.started_at
            ? new Date(execution.started_at).toLocaleString("en-IN")
            : "—"}
        </span>

        <span style={{ color: "#64748b" }}>Completed:</span>
        <span style={{ color: "#94a3b8" }}>
          {execution.completed_at
            ? new Date(execution.completed_at).toLocaleString("en-IN")
            : "—"}
        </span>

        <span style={{ color: "#64748b" }}>Steps:</span>
        <span style={{ color: "#94a3b8" }}>
          <span style={{ color: "#4ade80" }}>{successCount} successful</span>
          {waitingCount > 0 && (
            <span style={{ color: "#fdba74" }}> · {waitingCount} waiting</span>
          )}
          {failedCount > 0 && (
            <span style={{ color: "#f87171" }}> · {failedCount} failed</span>
          )}
          <span style={{ color: "#475569" }}> of {totalSteps} total</span>
        </span>
      </div>

      {execution.error_message && (
        <div
          style={{
            background: "#450a0a",
            border: "1px solid #dc2626",
            borderRadius: "6px",
            padding: "0.75rem",
            color: "#fca5a5",
            fontSize: "0.85rem",
            marginBottom: "1rem",
          }}
        >
          <strong>Error:</strong> {execution.error_message}
        </div>
      )}

      <div
        style={{
          background: "#0f172a",
          border: "1px solid #1e293b",
          borderRadius: "6px",
          padding: "0.75rem",
          fontSize: "0.82rem",
          color: "#64748b",
        }}
      >
        <strong style={{ color: "#94a3b8" }}>Portal Result:</strong>{" "}
        {portalResult ? (
          <pre
            style={{
              margin: "0.5rem 0 0",
              color: "#94a3b8",
              fontSize: "0.78rem",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {JSON.stringify(portalResult, null, 2)}
          </pre>
        ) : (
          <span style={{ fontStyle: "italic" }}>
            Only information actually obtained from the authorized portal session will appear here.
            No result has been fabricated.
          </span>
        )}
      </div>
    </div>
  );
}
