import { useState, ReactNode } from 'react';
import { Header } from '../components/layout/Header';
import { Sidebar } from '../components/layout/Sidebar';
import { Footer } from '../components/layout/Footer';

interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}

interface MainLayoutProps {
  children: ReactNode;
  title?: string;
  navItems?: NavItem[];
  activeHref?: string;
  onNavigate?: (href: string) => void;
}

export function MainLayout({
  children,
  title = 'AI Portal Automation',
  navItems = [],
  activeHref,
  onNavigate,
}: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background: '#0f172a',
      }}
    >
      <Header title={title} onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar
          items={navItems}
          activeHref={activeHref}
          onNavigate={onNavigate}
          isOpen={sidebarOpen}
        />

        <main
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '1.5rem 2rem',
            background: '#0f172a',
          }}
        >
          {children}
        </main>
      </div>

      <Footer />
    </div>
  );
}
