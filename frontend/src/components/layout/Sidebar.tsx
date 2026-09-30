interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}

interface SidebarProps {
  items: NavItem[];
  activeHref?: string;
  onNavigate?: (href: string) => void;
  isOpen?: boolean;
}

export function Sidebar({ items, activeHref, onNavigate, isOpen = true }: SidebarProps) {
  return (
    <aside
      style={{
        background: '#0f172a',
        borderRight: '1px solid #334155',
        width: isOpen ? '240px' : '0',
        maxWidth: '240px',
        padding: isOpen ? '1.5rem 0' : '0',
        overflow: 'hidden',
        transition: 'width 0.3s ease, padding 0.3s ease',
        position: 'relative',
        zIndex: 50,
      }}
    >
      <nav>
        {items.map((item) => (
          <a
            key={item.href}
            href={item.href}
            onClick={(e) => {
              e.preventDefault();
              onNavigate?.(item.href);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1.25rem',
              color: activeHref === item.href ? '#60a5fa' : '#94a3b8',
              textDecoration: 'none',
              fontSize: '0.9rem',
              borderLeft: activeHref === item.href ? '3px solid #3b82f6' : '3px solid transparent',
              background: activeHref === item.href ? '#1e3a5f' : 'transparent',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              position: 'relative',
            }}
            aria-current={activeHref === item.href ? 'page' : undefined}
          >
            <span style={{ fontSize: '1.1rem' }}>{item.icon}</span>
            <span style={{ flex: 1 }}>{item.label}</span>
            {item.badge && (
              <span
                style={{
                  background: '#ef4444',
                  color: '#fff',
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  borderRadius: '50%',
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {item.badge}
              </span>
            )}
          </a>
        ))}
      </nav>
    </aside>
  );
}
