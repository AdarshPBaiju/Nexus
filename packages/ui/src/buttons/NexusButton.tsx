'use client';
import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';
import { NexusText } from '../typography/NexusText';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface NexusButtonProps {
  readonly variant?: ButtonVariant;
  readonly size?: ButtonSize;
  readonly disabled?: boolean;
  readonly loading?: boolean;
  readonly onClick?: () => void;
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function NexusButton({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  children,
}: NexusButtonProps): React.JSX.Element {
  const isActionSurface = variant === 'primary' || variant === 'destructive';
  const surfaceRole: SurfaceRole =
    variant === 'destructive' ? 'destructive-action' : isActionSurface ? 'primary-action' : 'subtle';

  const paddingMap: Record<ButtonSize, string> = {
    sm: 'var(--nx-space-1) var(--nx-space-2)',
    md: 'var(--nx-space-2) var(--nx-space-4)',
    lg: 'var(--nx-space-3) var(--nx-space-6)',
  };

  const buttonStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--nx-space-2)',
    padding: paddingMap[size],
    borderRadius: '6px',
    border: variant === 'outline' ? '1px solid var(--nx-border-default)' : 'none',
    backgroundColor:
      variant === 'primary'
        ? 'var(--nx-action-primary)'
        : variant === 'destructive'
        ? 'var(--nx-action-destructive)'
        : variant === 'secondary'
        ? 'var(--nx-action-secondary)'
        : 'transparent',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.6 : 1,
    transition: 'background-color 0.15s ease',
  };

  return (
    <SurfaceProvider role={surfaceRole}>
      <button
        type="button"
        style={buttonStyle}
        disabled={disabled || loading}
        onClick={onClick}
        className={className}
      >
        {typeof children === 'string' ? (
          <NexusText variant="label">{children}</NexusText>
        ) : (
          children
        )}
      </button>
    </SurfaceProvider>
  );
}
