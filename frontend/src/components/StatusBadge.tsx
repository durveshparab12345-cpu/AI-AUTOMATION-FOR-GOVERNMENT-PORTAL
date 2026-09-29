import type { ExecutionStatus, StepStatus } from "../types";

type Status = ExecutionStatus | StepStatus;

const COLORS: Record<string, { bg: string; text: string }> = {
  PENDING:          { bg: "#334155", text: "#94a3b8" },
  RUNNING:          { bg: "#1e3a5f", text: "#60a5fa" },
  WAITING_FOR_HUMAN:{ bg: "#7c2d12", text: "#fdba74" },
  VALIDATING:       { bg: "#1e3a5f", text: "#a78bfa" },
  COMPLETED:        { bg: "#14532d", text: "#4ade80" },
  SUCCESS:          { bg: "#14532d", text: "#4ade80" },
  FAILED:           { bg: "#450a0a", text: "#f87171" },
  CANCELLED:        { bg: "#1c1917", text: "#78716c" },
  SKIPPED:          { bg: "#1c1917", text: "#78716c" },
};

interface Props {
  status: Status;
  size?: "sm" | "md";
}

export function StatusBadge({ status, size = "md" }: Props) {
  const colors = COLORS[status] ?? COLORS["PENDING"];
  const fontSize = size === "sm" ? "0.65rem" : "0.7rem";
  return (
    <span
      style={{
        display: "inline-block",
        background: colors.bg,
        color: colors.text,
        fontSize,
        fontWeight: 700,
        letterSpacing: "0.06em",
        padding: "2px 8px",
        borderRadius: "4px",
        whiteSpace: "nowrap",
      }}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
