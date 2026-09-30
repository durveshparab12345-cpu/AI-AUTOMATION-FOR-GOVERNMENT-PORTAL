import { Button } from '../components/common/Button';

interface NotFoundPageProps {
  onNavigate?: (page: string) => void;
}

export function NotFoundPage({ onNavigate }: NotFoundPageProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '80vh',
        padding: '2rem',
        textAlign: 'center',
      }}
    >
      <div style={{ fontSize: '5rem', marginBottom: '1rem' }}>404</div>
      <h1 style={{ color: '#f1f5f9', margin: 0, fontSize: '2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        Page Not Found
      </h1>
      <p style={{ color: '#64748b', fontSize: '1rem', marginBottom: '2rem' }}>
        The page you're looking for doesn't exist.
      </p>
      <Button variant="primary" onClick={() => onNavigate?.('dashboard')}>
        ← Back to Dashboard
      </Button>
    </div>
  );
}
