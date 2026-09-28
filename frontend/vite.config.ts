import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite configuration for the AI Portal Automation Platform frontend.
 *
 * The proxy forwards /api requests to the FastAPI backend during development
 * so the frontend dev server and API run on different ports without CORS issues.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy API calls to the FastAPI backend in development.
      // Production deployments should handle this at the reverse-proxy level.
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
