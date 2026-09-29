// Human-in-the-loop dialog — shown when execution enters WAITING_FOR_HUMAN.
// Provides clear reason and two actions: Continue or Stop.
import { useState } from "react";

interface Props {
  reason: string;
  executionId: string;
  onContinue: (note: string) => Promise<void>;
  onCancel: () => Promise<void>;
  loading: boolean;
}

export function HumanActionDialog({
  reason,
  onContinue,
  onCancel,
  loading,
}: Props) {
  const [note, setNote] = useState("");

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="human-action-title"
      style={{
        background: "#7c2d12",
        border: "2px solid #f97316",
        borderRadius: "10px",
        padding: "1.5rem",
        marginTop: "1rem",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.6rem",
          marginBottom: "0.75rem",
        }}
      >
        <span style={{ fontSize: "1.4rem" }} aria-hidden="true">
          🙋
        </span>
        <h3
          id="human-action-title"
          style={{ color: "#fed7aa", margin: 0, fontSize: "1rem" }}
        >
          Human Action Required
        </h3>
      </div>

      <p
        style={{
          color: "#fdba74",
          fontSize: "0.9rem",
          lineHeight: 1.6,
          marginBottom: "1rem",
        }}
      >
        {reason}
      </p>

      <label
        htmlFor="operator-note"
        style={{
          display: "block",
          color: "#fed7aa",
          fontSize: "0.8rem",
          marginBottom: "0.3rem",
        }}
      >
        Operator note (optional):
      </label>
      <textarea
        id="operator-note"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Describe what action was taken..."
        rows={2}
        style={{
          width: "100%",
          background: "#1c0a00",
          color: "#fed7aa",
          border: "1px solid #f97316",
          borderRadius: "6px",
          padding: "0.5rem",
          fontSize: "0.85rem",
          resize: "vertical",
          marginBottom: "1rem",
          boxSizing: "border-box",
        }}
      />

      <div style={{ display: "flex", gap: "0.75rem" }}>
        <button
          onClick={() => onContinue(note)}
          disabled={loading}
          aria-label="Continue workflow after completing required action"
          style={{
            flex: 1,
            background: loading ? "#78350f" : "#f97316",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            padding: "0.6rem 1rem",
            fontWeight: 700,
            fontSize: "0.9rem",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Resuming…" : "✓ Continue"}
        </button>
        <button
          onClick={onCancel}
          disabled={loading}
          aria-label="Stop and cancel the workflow"
          style={{
            flex: 1,
            background: "transparent",
            color: "#f87171",
            border: "2px solid #f87171",
            borderRadius: "6px",
            padding: "0.6rem 1rem",
            fontWeight: 700,
            fontSize: "0.9rem",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          ✕ Stop Workflow
        </button>
      </div>
    </div>
  );
}
