import { FormEvent, useState } from "react";
import { login, setToken } from "../services/api";
import type { AuthState } from "../types";

interface Props {
  onLogin: (auth: AuthState) => void;
}

export function LoginPage({ onLogin }: Props) {
  const [email, setEmail] = useState("demo@ai-portal-demo.local");
  const [password, setPassword] = useState("DemoPassword@2026");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const resp = await login(email, password);
      setToken(resp.access_token);
      onLogin({
        token: resp.access_token,
        email: resp.user_email,
        name: resp.user_name,
        organizationId: resp.organization_id,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "2rem",
      }}
    >
      <div
        style={{
          background: "#1e293b",
          border: "1px solid #334155",
          borderRadius: "12px",
          padding: "2.5rem 3rem",
          width: "100%",
          maxWidth: "420px",
        }}
      >
        <h1
          style={{
            color: "#f1f5f9",
            fontSize: "1.4rem",
            fontWeight: 700,
            marginBottom: "0.25rem",
          }}
        >
          AI Portal Automation
        </h1>
        <p style={{ color: "#64748b", fontSize: "0.9rem", marginBottom: "2rem" }}>
          Stage 2A — PM-JAY Live Prototype
        </p>

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: "1rem" }}>
            <label
              htmlFor="email"
              style={{ display: "block", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "0.35rem" }}
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="username"
              style={{
                width: "100%",
                background: "#0f172a",
                color: "#f1f5f9",
                border: "1px solid #334155",
                borderRadius: "6px",
                padding: "0.6rem 0.75rem",
                fontSize: "0.9rem",
                boxSizing: "border-box",
              }}
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              htmlFor="password"
              style={{ display: "block", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "0.35rem" }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              style={{
                width: "100%",
                background: "#0f172a",
                color: "#f1f5f9",
                border: "1px solid #334155",
                borderRadius: "6px",
                padding: "0.6rem 0.75rem",
                fontSize: "0.9rem",
                boxSizing: "border-box",
              }}
            />
          </div>

          {error && (
            <div
              role="alert"
              style={{
                background: "#450a0a",
                color: "#fca5a5",
                borderRadius: "6px",
                padding: "0.6rem 0.75rem",
                fontSize: "0.85rem",
                marginBottom: "1rem",
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              background: loading ? "#1e3a5f" : "#3b82f6",
              color: "#fff",
              border: "none",
              borderRadius: "8px",
              padding: "0.75rem",
              fontWeight: 700,
              fontSize: "1rem",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div
          style={{
            marginTop: "1.5rem",
            padding: "0.75rem",
            background: "#0f172a",
            borderRadius: "6px",
            fontSize: "0.78rem",
            color: "#475569",
          }}
        >
          <strong style={{ color: "#64748b" }}>Demo credentials:</strong>
          <br />
          {email} / {password}
        </div>
      </div>
    </main>
  );
}
