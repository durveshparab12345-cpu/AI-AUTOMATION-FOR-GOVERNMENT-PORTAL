export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      style={{
        background: '#0f172a',
        borderTop: '1px solid #334155',
        padding: '1.5rem 1.5rem',
        textAlign: 'center',
        marginTop: 'auto',
      }}
    >
      <div style={{ color: '#64748b', fontSize: '0.85rem' }}>
        <p style={{ margin: '0 0 0.5rem' }}>
          AI Portal Automation Platform v0.2.0 — Stage 2A
        </p>
        <p style={{ margin: 0 }}>
          © {currentYear} All rights reserved. | Built with React + TypeScript
        </p>
      </div>
    </footer>
  );
}
