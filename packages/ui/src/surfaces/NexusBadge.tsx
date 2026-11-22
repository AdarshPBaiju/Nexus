'use client';
import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';
import { NexusText } from '../typography/NexusText';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

export interface NexusBadgeProps {
  readonly variant?: BadgeVariant;
  readonly label?: string;
  readonly children?: React.ReactNode;
  readonly dot?: boolean;
  readonly className?: string;
  readonly style?: React.CSSProperties;
}

const VARIANT_SURFACE: Record<BadgeVariant, SurfaceRole> = {
  success: 'status-success-subtle',
  warning: 'status-warning-subtle',
  danger: 'status-danger-subtle',
  info: 'status-info-subtle',
  neutral: 'subtle',
};

const DOT_COLOR: Record<BadgeVariant, string> = {
  success: 'var(--nx-status-success)',
  warning: 'var(--nx-status-warning)',
  danger: 'var(--nx-status-danger)',
  info: 'var(--nx-status-info)',
  neutral: 'var(--nx-text-muted)',
};

export function NexusBadge({
  variant = 'neutral',
  label,
  children,
  dot = false,
  className = '',
  style = {},
}: NexusBadgeProps): React.JSX.Element {
  const badgeStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '5px',
    padding: '2px 8px',
    borderRadius: '9999px',
    whiteSpace: 'nowrap',
    backgroundColor:
      variant === 'neutral'
        ? 'var(--nx-surface-subtle)'
        : `var(--nx-status-${variant}-subtle)`,
    border: `1px solid var(--nx-border-subtle)`,
    ...style,
  };

  return (
    <SurfaceProvider role={VARIANT_SURFACE[variant]}>
      <span style={badgeStyle} className={className}>
        {dot && (
          <span
            aria-hidden="true"
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '9999px',
              backgroundColor: DOT_COLOR[variant],
              flexShrink: 0,
            }}
          />
        )}
        <NexusText variant="caption" style={{ fontWeight: 600, letterSpacing: '0.01em' }}>
          {children ?? label}
        </NexusText>
      </span>
    </SurfaceProvider>
  );
}
