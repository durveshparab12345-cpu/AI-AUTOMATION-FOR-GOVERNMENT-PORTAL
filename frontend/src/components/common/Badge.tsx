import type { CaseStatus, WorkflowStatus, PortalStatus, ExecutionStatus, UserRole } from '../../types';

type Status = CaseStatus | WorkflowStatus | PortalStatus | ExecutionStatus | 'PENDING' | 'ACTIVE' | 'INACTIVE' | UserRole;

interface BadgeProps {
  status: Status;
  label?: string;
}

const statusColors: Record<Status, { bg: string; text: string }> = {
  // Execution statuses
  PENDING: { bg: '#1e3a8a', text: '#93c5fd' },
  RUNNING: { bg: '#1e3a0b', text: '#bfdbfe' },
  WAITING_FOR_HUMAN: { bg: '#78350f', text: '#fde047' },
  VALIDATING: { bg: '#1e3a0b', text: '#bfdbfe' },
  COMPLETED: { bg: '#064e3b', text: '#6ee7b7' },
  FAILED: { bg: '#7c2d12', text: '#fed7aa' },
  CANCELLED: { bg: '#3f0f0f', text: '#fca5a5' },

  // Case statuses
  INITIATED: { bg: '#1e3a8a', text: '#93c5fd' },
  IN_PROGRESS: { bg: '#1e3a0b', text: '#bfdbfe' },
  PENDING_APPROVAL: { bg: '#78350f', text: '#fde047' },
  APPROVED: { bg: '#064e3b', text: '#6ee7b7' },
  PROCESSING: { bg: '#1e3a0b', text: '#bfdbfe' },
  REJECTED: { bg: '#7c2d12', text: '#fed7aa' },

  // Workflow statuses
  DRAFT: { bg: '#3f3f46', text: '#d4d4d8' },
  PUBLISHED: { bg: '#064e3b', text: '#6ee7b7' },
  ARCHIVED: { bg: '#3f0f0f', text: '#fca5a5' },

  // Portal statuses
  ACTIVE: { bg: '#064e3b', text: '#6ee7b7' },
  INACTIVE: { bg: '#3f0f0f', text: '#fca5a5' },
  MAINTENANCE: { bg: '#78350f', text: '#fde047' },

  // User roles
  ADMIN: { bg: '#7c2d12', text: '#fed7aa' },
  SUPERVISOR: { bg: '#1e3a8a', text: '#93c5fd' },
  OPERATOR: { bg: '#064e3b', text: '#6ee7b7' },
  VIEWER: { bg: '#3f3f46', text: '#d4d4d8' },
};

export function Badge({ status, label }: BadgeProps) {
  const colors = statusColors[status] || { bg: '#1e293b', text: '#94a3b8' };
  const displayLabel = label || status;

  return (
    <span
      style={{
        display: 'inline-block',
        background: colors.bg,
        color: colors.text,
        padding: '0.25rem 0.75rem',
        borderRadius: '4px',
        fontSize: '0.75rem',
        fontWeight: 700,
        letterSpacing: '0.05em',
        textTransform: 'uppercase',
      }}
    >
      {displayLabel}
    </span>
  );
}
