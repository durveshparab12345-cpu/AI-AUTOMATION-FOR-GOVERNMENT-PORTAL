import "./App.css";

/**
 * Root application component.
 *
 * Stage 1: Renders the platform foundation page only.
 * Authentication, dashboard, workflow UI, and portal management
 * will be added in future stages.
 */
function App() {
  return (
    <main className="app-root">
      <div className="foundation-card">
        <div className="badge">Stage 1</div>
        <h1 className="platform-title">AI Portal Automation Platform</h1>
        <p className="stage-label">Stage 1 — System Foundation</p>
        <p className="stage-description">
          The platform foundation is in place. Authentication, workflow
          management, and portal automation will be available in future stages.
        </p>
        <div className="status-indicator">
          <span className="status-dot" aria-hidden="true" />
          <span>Backend API: operational</span>
        </div>
      </div>
    </main>
  );
}

export default App;
