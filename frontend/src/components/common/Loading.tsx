interface LoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function Loading({ message = 'Loading...', size = 'md' }: LoadingProps) {
  const sizeMap = {
    sm: '24px',
    md: '40px',
    lg: '60px',
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem',
        color: '#64748b',
      }}
    >
      <div
        style={{
          width: sizeMap[size],
          height: sizeMap[size],
          border: '3px solid #334155',
          borderTop: '3px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          marginBottom: '1rem',
        }}
      />
      {message && <p style={{ margin: 0, fontSize: '0.9rem' }}>{message}</p>}
    </div>
  );
}

// Global animation styles can be added to a stylesheet or CSS module
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(style);
