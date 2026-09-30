import { ButtonHTMLAttributes, ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: ReactNode;
  isLoading?: boolean;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  isLoading,
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = {
    fontWeight: 700,
    border: 'none',
    borderRadius: '8px',
    cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    fontSize: size === 'sm' ? '0.8rem' : size === 'lg' ? '1rem' : '0.9rem',
    padding:
      size === 'sm'
        ? '0.4rem 0.75rem'
        : size === 'lg'
          ? '0.75rem 1.5rem'
          : '0.6rem 1rem',
  };

  const variantStyles = {
    primary: {
      background: disabled || isLoading ? '#334155' : '#3b82f6',
      color: '#fff',
      '&:hover': { background: '#2563eb' },
    },
    secondary: {
      background: 'transparent',
      color: '#3b82f6',
      border: '1px solid #3b82f6',
      '&:hover': { background: '#1e3a5f' },
    },
    danger: {
      background: disabled || isLoading ? '#334155' : '#ef4444',
      color: '#fff',
      '&:hover': { background: '#dc2626' },
    },
    ghost: {
      background: 'transparent',
      color: '#94a3b8',
      '&:hover': { background: '#1e293b' },
    },
  };

  const selectedVariant = variantStyles[variant];

  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      style={{
        ...baseStyles,
        ...selectedVariant,
      }}
    >
      {isLoading ? '…' : children}
    </button>
  );
}
