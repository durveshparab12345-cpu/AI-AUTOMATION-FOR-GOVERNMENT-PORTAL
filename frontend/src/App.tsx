import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { DemoModeBadge } from "./components/DemoModeBadge";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import { MainLayout } from "./layouts/MainLayout";
import { LoginPage } from "./pages/LoginPage";
import { PMJayDemoPage } from "./pages/PMJayDemoPage";
import { DashboardPage } from "./pages/DashboardPage";
import { PortalsPage } from "./pages/PortalsPage";
import { WorkflowsPage } from "./pages/WorkflowsPage";
import { CasesPage } from "./pages/CasesPage";
import { AutomationsPage } from "./pages/AutomationsPage";
import { SettingsPage } from "./pages/SettingsPage";
import { UserProfilePage } from "./pages/UserProfilePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import "./App.css";

type Page = 'dashboard' | 'demo' | 'portals' | 'workflows' | 'cases' | 'automations' | 'settings' | 'profile' | 'not-found';

function AppContent() {
  const { auth, setAuth, logout, isAuthenticated } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');

  if (!isAuthenticated) {
    return <LoginPage onLogin={setAuth} />;
  }

  const navItems = [
    { label: 'Dashboard', href: 'dashboard', icon: '📊' },
    { label: 'Demo', href: 'demo', icon: '🚀' },
    { label: 'Portals', href: 'portals', icon: '🌐' },
    { label: 'Workflows', href: 'workflows', icon: '⚙️' },
    { label: 'Cases', href: 'cases', icon: '📋' },
    { label: 'Automations', href: 'automations', icon: '⚡' },
    { label: 'Settings', href: 'settings', icon: '⚙️', badge: 0 },
    { label: 'Profile', href: 'profile', icon: '👤' },
  ];

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage onNavigate={setCurrentPage} />;
      case 'demo':
        return <PMJayDemoPage auth={auth} onLogout={logout} />;
      case 'portals':
        return <PortalsPage />;
      case 'workflows':
        return <WorkflowsPage />;
      case 'cases':
        return <CasesPage />;
      case 'automations':
        return <AutomationsPage />;
      case 'settings':
        return <SettingsPage />;
      case 'profile':
        return <UserProfilePage />;
      case 'not-found':
        return <NotFoundPage onNavigate={setCurrentPage} />;
      default:
        return <DashboardPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <ErrorBoundary>
      <MainLayout
        title="AI Portal Automation"
        navItems={navItems}
        activeHref={currentPage}
        onNavigate={(href) => {
          const page = href as Page;
          setCurrentPage(page);
        }}
      >
        {renderPage()}
      </MainLayout>
    </ErrorBoundary>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <DemoModeBadge />
      <AppContent />
    </AuthProvider>
  );
}
