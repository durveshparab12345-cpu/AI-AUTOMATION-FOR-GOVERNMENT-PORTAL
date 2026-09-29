// Left-panel workflow step tracker
import type { ExecutionStep } from "../types";
import { StatusBadge } from "./StatusBadge";

const STEP_ICONS: Record<string, string> = {
  SUCCESS: "✓",
  RUNNING: "→",
  WAITING_FOR_HUMAN: "🙋",
  FAILED: "✕",
  PENDING: "○",
  SKIPPED: "–",
};

interface Props {
  steps: ExecutionStep[];
  currentStep: number;
}

export function WorkflowStepList({ steps, currentStep }: Props) {
  if (steps.length === 0) {
    // Show placeholder steps before execution starts
    const placeholders = [
      "Initialize workflow",
      "Open PM-JAY portal",
      "Authenticate operator",
      "Navigate to beneficiary section",
      "Search for beneficiary",
      "Read beneficiary information",
      "Map and validate case data",
      "Human confirmation before submission",
      "Capture portal result",
      "Complete",
    ];
    return (
      <ol style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {placeholders.map((name, i) => (
          <li
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              padding: "0.45rem 0",
              borderBottom: "1px solid #1e293b",
              color: "#475569",
              fontSize: "0.85rem",
            }}
          >
            <span style={{ width: "1.2rem", textAlign: "center" }}>○</span>
            {name}
          </li>
        ))}
      </ol>
    );
  }

  return (
    <ol style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {steps.map((step) => {
        const isActive = step.step_number === currentStep;
        const icon = STEP_ICONS[step.status] ?? "○";
        return (
          <li
            key={step.id}
            aria-current={isActive ? "step" : undefined}
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "0.6rem",
              padding: "0.5rem 0",
              borderBottom: "1px solid #1e293b",
              fontSize: "0.85rem",
              color:
                step.status === "SUCCESS"
                  ? "#4ade80"
                  : step.status === "FAILED"
                    ? "#f87171"
                    : step.status === "WAITING_FOR_HUMAN"
                      ? "#fdba74"
                      : step.status === "RUNNING"
                        ? "#93c5fd"
                        : "#64748b",
              fontWeight: isActive ? 700 : 400,
            }}
          >
            <span
              style={{ width: "1.2rem", textAlign: "center", flexShrink: 0 }}
            >
              {icon}
            </span>
            <span style={{ flex: 1 }}>
              {step.step_name}
              {step.message && step.status !== "PENDING" && (
                <div
                  style={{
                    fontSize: "0.75rem",
                    color: "#64748b",
                    marginTop: "2px",
                  }}
                >
                  {step.message}
                </div>
              )}
            </span>
            <StatusBadge status={step.status} size="sm" />
          </li>
        );
      })}
    </ol>
  );
}
