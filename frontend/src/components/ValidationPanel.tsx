// Validation results panel
import type { ValidationCheck } from "../types";

interface Props {
  checks: ValidationCheck[];
  passed: boolean;
}

export function ValidationPanel({ checks, passed }: Props) {
  return (
    <div
      style={{
        background: passed ? "#052e16" : "#450a0a",
        border: `1px solid ${passed ? "#16a34a" : "#dc2626"}`,
        borderRadius: "8px",
        padding: "1rem",
      }}
    >
      <h4
        style={{
          color: passed ? "#4ade80" : "#f87171",
          margin: "0 0 0.75rem",
          fontSize: "0.9rem",
        }}
      >
        {passed ? "✓ Validation Passed" : "✕ Validation Failed"}
      </h4>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {checks.map((c) => (
          <li
            key={c.name}
            style={{
              display: "flex",
              gap: "0.5rem",
              padding: "0.3rem 0",
              borderBottom: "1px solid #1e293b",
              fontSize: "0.85rem",
              alignItems: "flex-start",
            }}
          >
            <span
              style={{
                color: c.passed ? "#4ade80" : "#f87171",
                flexShrink: 0,
                width: "1rem",
              }}
            >
              {c.passed ? "✓" : "✕"}
            </span>
            <span style={{ flex: 1, color: "#cbd5e1" }}>{c.name}</span>
            <span
              style={{
                color: c.passed ? "#64748b" : "#fca5a5",
                fontSize: "0.78rem",
              }}
            >
              {c.message}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
