// Visual data mapping panel — shows internal field → portal field mapping
import type { DemoCase, FieldMapping } from "../types";

function buildMappings(c: DemoCase): FieldMapping[] {
  return [
    {
      internalLabel: "Demo Patient Name",
      internalValue: c.demo_patient_name,
      portalLabel: "Beneficiary Name (portal field — unverified)",
    },
    {
      internalLabel: "Demo Beneficiary ID",
      internalValue: c.demo_beneficiary_id,
      portalLabel: "Beneficiary ID (portal field — unverified)",
    },
    {
      internalLabel: "Date of Birth",
      internalValue: c.demo_dob,
      portalLabel: "DOB (portal field — unverified)",
    },
    {
      internalLabel: "Hospital Code",
      internalValue: c.demo_hospital_code,
      portalLabel: "Empanelled Hospital Code (portal field — unverified)",
    },
    {
      internalLabel: "Procedure Code",
      internalValue: c.demo_procedure_code,
      portalLabel: "HBP Package Code (portal field — unverified)",
    },
    {
      internalLabel: "Claim Amount",
      internalValue: `₹${Number(c.demo_amount).toLocaleString("en-IN")}`,
      portalLabel: "Claimed Amount (portal field — unverified)",
    },
  ];
}

interface Props {
  demoCase: DemoCase;
}

export function DataMappingPanel({ demoCase }: Props) {
  const mappings = buildMappings(demoCase);

  return (
    <div
      style={{
        background: "#0f172a",
        border: "1px solid #1e293b",
        borderRadius: "8px",
        padding: "1rem",
      }}
    >
      <h4 style={{ color: "#94a3b8", margin: "0 0 0.75rem", fontSize: "0.85rem", letterSpacing: "0.05em" }}>
        FIELD MAPPING
      </h4>
      <p style={{ color: "#475569", fontSize: "0.75rem", margin: "0 0 0.75rem" }}>
        Portal field selectors are marked UNVERIFIED — confirmed only in an authorized portal session.
      </p>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
        <thead>
          <tr style={{ color: "#475569", fontSize: "0.72rem" }}>
            <th style={{ textAlign: "left", padding: "0.25rem 0", borderBottom: "1px solid #1e293b", fontWeight: 600 }}>INTERNAL FIELD</th>
            <th style={{ textAlign: "center", padding: "0.25rem 0.5rem", color: "#3b82f6" }}>↓</th>
            <th style={{ textAlign: "left", padding: "0.25rem 0", borderBottom: "1px solid #1e293b", fontWeight: 600 }}>PORTAL FIELD</th>
          </tr>
        </thead>
        <tbody>
          {mappings.map((m) => (
            <tr key={m.internalLabel}>
              <td style={{ padding: "0.35rem 0", borderBottom: "1px solid #0f172a", color: "#cbd5e1", verticalAlign: "top" }}>
                <div style={{ fontSize: "0.72rem", color: "#64748b" }}>{m.internalLabel}</div>
                <div style={{ color: "#f1f5f9", fontWeight: 500 }}>{m.internalValue}</div>
              </td>
              <td style={{ textAlign: "center", color: "#3b82f6", fontWeight: 700 }}>→</td>
              <td style={{ padding: "0.35rem 0", borderBottom: "1px solid #0f172a", color: "#94a3b8", verticalAlign: "top", fontSize: "0.8rem" }}>
                {m.portalLabel}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
