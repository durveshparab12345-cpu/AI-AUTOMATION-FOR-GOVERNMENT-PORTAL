import { useEffect } from 'react';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose?: () => void;
  isVisible?: boolean;
}

const typeStyles: Record<ToastType, { bg: string; border: string; text: string; icon: string }> = {
  success: {
    bg: '#064e3b',
    border: '1px solid #10b981',
    text: '#6ee7b7',
    icon: '✓',
  },
  error: {
    bg: '#7c2d12',
    border: '1px solid #f87171',
    text: '#fca5a5',
    icon: '✕',
  },
  info: {
    bg: '#1e3a8a',
    border: '1px solid #3b82f6',
    text: '#93c5fd',
    icon: 'ⓘ',
  },
  warning: {
    bg: '#78350f',
    border: '1px solid #fbbf24',
    text: '#fde047',
    icon: '⚠',
  },
};

export function Toast({
  message,
  type = 'info',
  duration = 3000,
  onClose,
  isVisible = true,
}: ToastProps) {
  useEffect(() => {
    if (!isVisible || !onClose || duration === 0) return;

    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [isVisible, duration, onClose]);

  if (!isVisible) return null;

  const style = typeStyles[type];

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        background: style.bg,
        border: style.border,
        color: style.text,
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        fontSize: '0.9rem',
        zIndex: 2000,
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
        animation: 'slideIn 0.3s ease',
      }}
    >
      <span style={{ fontSize: '1.1rem' }}>{style.icon}</span>
      <span>{message}</span>
    </div>
  );
}
