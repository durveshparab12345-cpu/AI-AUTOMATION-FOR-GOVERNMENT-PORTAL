import { TextareaHTMLAttributes } from 'react';

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

export function TextAreaField({
  label,
  error,
  helperText,
  fullWidth = true,
  ...props
}: TextAreaFieldProps) {
  return (
    <div style={{ width: fullWidth ? '100%' : 'auto' }}>
      {label && (
        <label
          htmlFor={props.id}
          style={{
            display: 'block',
            color: '#94a3b8',
            fontSize: '0.85rem',
            fontWeight: 600,
            marginBottom: '0.35rem',
          }}
        >
          {label}
        </label>
      )}
      <textarea
        {...props}
        style={{
          width: '100%',
          background: '#0f172a',
          color: '#f1f5f9',
          border: `1px solid ${error ? '#f87171' : '#334155'}`,
          borderRadius: '6px',
          padding: '0.6rem 0.75rem',
          fontSize: '0.9rem',
          fontFamily: 'inherit',
          boxSizing: 'border-box',
          minHeight: '100px',
          resize: 'vertical',
        }}
      />
      {error && (
        <p style={{ color: '#f87171', fontSize: '0.75rem', margin: '0.25rem 0 0', fontWeight: 500 }}>
          {error}
        </p>
      )}
      {helperText && !error && (
        <p style={{ color: '#64748b', fontSize: '0.75rem', margin: '0.25rem 0 0' }}>
          {helperText}
        </p>
      )}
    </div>
  );
}
