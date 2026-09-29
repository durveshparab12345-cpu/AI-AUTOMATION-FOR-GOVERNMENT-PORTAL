import { useState } from "react";
import { DemoModeBadge } from "./components/DemoModeBadge";
import { LoginPage } from "./pages/LoginPage";
import { PMJayDemoPage } from "./pages/PMJayDemoPage";
import type { AuthState } from "./types";
import "./App.css";

export default function App() {
  const [auth, setAuth] = useState<AuthState>({
    token: null,
    email: null,
    name: null,
    organizationId: null,
  });

  function handleLogout() {
    setAuth({ token: null, email: null, name: null, organizationId: null });
  }

  return (
    <>
      <DemoModeBadge />
      <div style={{ paddingTop: "32px" }}>
        {!auth.token ? (
          <LoginPage onLogin={setAuth} />
        ) : (
          <PMJayDemoPage auth={auth} onLogout={handleLogout} />
        )}
      </div>
    </>
  );
}
