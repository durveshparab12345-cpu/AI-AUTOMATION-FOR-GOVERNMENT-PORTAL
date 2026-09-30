import { ReactNode } from 'react';

interface FormSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  columns?: 1 | 2 | 3;
}

export function FormSection({
  title,
  description,
  children,
  columns = 1,
}: FormSectionProps) {
  return (
    <div style={{ marginBottom: '1.5rem' }}>
      <div style={{ marginBottom: '1rem' }}>
        <h3 style={{ color: '#f1f5f9', margin: '0 0 0.25rem', fontSize: '0.95rem', fontWeight: 700 }}>
          {title}
        </h3>
        {description && (
          <p style={{ color: '#64748b', margin: 0, fontSize: '0.8rem' }}>{description}</p>
        )}
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${columns}, 1fr)`,
          gap: '1rem',
        }}
      >
        {children}
      </div>
    </div>
  );
}
