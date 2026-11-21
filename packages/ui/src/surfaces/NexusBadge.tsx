import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';
import { NexusText } from '../typography/NexusText';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

export interface NexusBadgeProps {
  readonly variant?: BadgeVariant;
  readonly label: string;
  readonly className?: string;
}

export function NexusBadge({
  variant = 'neutral',
  label,
  className = '',
}: NexusBadgeProps): React.JSX.Element {
  const surfaceRole: SurfaceRole =
    variant === 'success'
      ? 'status-success-subtle'
      : variant === 'warning'
      ? 'status-warning-subtle'
      : variant === 'danger'
      ? 'status-danger-subtle'
      : variant === 'info'
      ? 'status-info-subtle'
      : 'subtle';

  const badgeStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '2px 8px',
    borderRadius: '9999px',
    backgroundColor:
      variant === 'neutral' ? 'var(--nx-surface-subtle)' : `var(--nx-status-${variant}-subtle)`,
    border: `1px solid var(--nx-border-subtle)`,
  };

  return (
    <SurfaceProvider role={surfaceRole}>
      <span style={badgeStyle} className={className}>
        <NexusText variant="caption">{label}</NexusText>
      </span>
    </SurfaceProvider>
  );
}
