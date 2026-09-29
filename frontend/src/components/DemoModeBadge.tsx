// Persistent DEMO MODE banner — always visible during the prototype.
export function DemoModeBadge() {
  return (
    <div
      role="status"
      aria-label="Demo mode active — synthetic data only"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: "#b45309",
        color: "#fff",
        textAlign: "center",
        fontSize: "0.75rem",
        fontWeight: 700,
        letterSpacing: "0.06em",
        padding: "6px 0",
      }}
    >
      ⚠ DEMO MODE — SYNTHETIC DATA ONLY — NOT FOR PRODUCTION USE
    </div>
  );
}
