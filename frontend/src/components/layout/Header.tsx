import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  title?: string;
  onMenuClick?: () => void;
}

export function Header({ title = 'AI Portal Automation', onMenuClick }: HeaderProps) {
  const { auth, logout } = useAuth();

  return (
    <header
      style={{
        background: '#1e293b',
        borderBottom: '1px solid #334155',
        padding: '1rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        {onMenuClick && (
          <button
            onClick={onMenuClick}
            aria-label="Toggle menu"
            style={{
              background: 'transparent',
              border: '1px solid #334155',
              color: '#94a3b8',
              borderRadius: '6px',
              padding: '0.5rem 0.75rem',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
          >
            ☰
          </button>
        )}
        <h1 style={{ color: '#f1f5f9', fontSize: '1.1rem', fontWeight: 700, margin: 0 }}>
          {title}
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: '#3b82f6',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontWeight: 700,
              fontSize: '0.9rem',
            }}
          >
            {auth.name?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div>
            <div style={{ color: '#f1f5f9', fontSize: '0.85rem', fontWeight: 600 }}>
              {auth.name || 'User'}
            </div>
            <div style={{ color: '#64748b', fontSize: '0.75rem' }}>{auth.email || 'No email'}</div>
          </div>
        </div>

        <button
          onClick={logout}
          style={{
            background: 'transparent',
            color: '#64748b',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '0.4rem 0.9rem',
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
          aria-label="Sign out"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
