import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  footer?: ReactNode;
  padding?: string;
  clickable?: boolean;
  onClick?: () => void;
  hoverable?: boolean;
  style?: React.CSSProperties;
}

export function Card({
  children,
  title,
  subtitle,
  footer,
  padding = '1.5rem',
  clickable = false,
  onClick,
  hoverable = false,
  style = {},
}: CardProps) {
  return (
    <div
      onClick={clickable ? onClick : undefined}
      style={{
        background: '#1e293b',
        border: '1px solid #334155',
        borderRadius: '10px',
        padding,
        cursor: clickable ? 'pointer' : 'default',
        transition: hoverable || clickable ? 'all 0.2s ease' : 'none',
        ...style,
      }}
      onMouseEnter={(e) => {
        if (clickable || hoverable) {
          (e.currentTarget as HTMLElement).style.borderColor = '#475569';
          (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
        }
      }}
      onMouseLeave={(e) => {
        if (clickable || hoverable) {
          (e.currentTarget as HTMLElement).style.borderColor = '#334155';
          (e.currentTarget as HTMLElement).style.boxShadow = 'none';
        }
      }}
    >
      {title && (
        <h3
          style={{
            color: '#f1f5f9',
            margin: '0 0 0.5rem',
            fontSize: '1rem',
            fontWeight: 700,
          }}
        >
          {title}
        </h3>
      )}
      {subtitle && (
        <p style={{ color: '#64748b', margin: '0 0 1rem', fontSize: '0.85rem' }}>
          {subtitle}
        </p>
      )}
      <div style={{ color: '#cbd5e1' }}>{children}</div>
      {footer && (
        <div
          style={{
            marginTop: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid #334155',
            color: '#94a3b8',
            fontSize: '0.85rem',
          }}
        >
          {footer}
        </div>
      )}
    </div>
  );
}
