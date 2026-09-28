# AI Portal Automation Platform — Frontend

React + TypeScript + Vite frontend for the AI Portal Automation Platform.

## Stage 1 Scope

This is the minimal foundation. The current page displays the platform name
and confirms the system is at Stage 1. No authentication, dashboard, or
workflow UI is implemented yet.

## Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Available at: http://localhost:5173

## Directory Structure

```
src/
├── App.tsx           # Root component
├── App.css           # Foundation page styles
├── main.tsx          # Entry point
├── components/       # Shared UI components (Stage 2+)
├── pages/            # Page-level components (Stage 2+)
├── layouts/          # Layout wrappers (Stage 2+)
├── services/         # API client services (Stage 2+)
├── hooks/            # Custom React hooks (Stage 2+)
└── types/            # TypeScript type definitions (Stage 2+)
```

## Build

```bash
npm run build       # Compile TypeScript + bundle with Vite
npm run preview     # Preview the production build locally
npm run type-check  # Run TypeScript type checking without emitting files
```
