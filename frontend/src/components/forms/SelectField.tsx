import { SelectHTMLAttributes } from 'react';

interface SelectOption {
  value: string | number;
  label: string;
}

interface SelectFieldProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  placeholder?: string;
}

export function SelectField({
  label,
  options,
  error,
  helperText,
  fullWidth = false,
  placeholder,
  ...props
}: SelectFieldProps) {
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
      <select
        {...props}
        style={{
          width: '100%',
          background: '#0f172a',
          color: '#f1f5f9',
          border: `1px solid ${error ? '#f87171' : '#334155'}`,
          borderRadius: '6px',
          padding: '0.6rem 0.75rem',
          fontSize: '0.9rem',
          boxSizing: 'border-box',
          cursor: 'pointer',
        }}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
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
