'use client';
import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';
import { NexusText } from '../typography/NexusText';

export type ButtonVariant =
  | 'primary'
  | 'secondary'
  | 'outline'
  | 'ghost'
  | 'destructive'
  | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface NexusButtonProps {
  readonly variant?: ButtonVariant;
  readonly size?: ButtonSize;
  readonly type?: 'button' | 'submit' | 'reset';
  readonly title?: string;
  readonly ariaLabel?: string;
  readonly disabled?: boolean;
  readonly loading?: boolean;
  readonly onClick?: () => void;
  readonly className?: string;
  readonly style?: React.CSSProperties;
  readonly children: React.ReactNode;
}

const PADDING: Record<ButtonSize, string> = {
  sm: '4px 10px',
  md: '7px 14px',
  lg: '10px 20px',
};

const HEIGHT: Record<ButtonSize, string> = {
  sm: '28px',
  md: '34px',
  lg: '40px',
};

export function NexusButton({
  variant = 'primary',
  size = 'md',
  type = 'button',
  title,
  ariaLabel,
  disabled = false,
  loading = false,
  onClick,
  className = '',
  style = {},
  children,
}: NexusButtonProps): React.JSX.Element {
  const isDestructive = variant === 'destructive' || variant === 'danger';
  const isActionSurface = variant === 'primary' || isDestructive;
  const surfaceRole: SurfaceRole = isDestructive
    ? 'destructive-action'
    : isActionSurface
    ? 'primary-action'
    : 'subtle';

  const isDisabled = disabled || loading;

  const buttonStyle: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 'var(--nx-space-2)',
    height: HEIGHT[size],
    padding: PADDING[size],
    borderRadius: '6px',
    border:
      variant === 'outline'
        ? '1px solid var(--nx-border-default)'
        : isDestructive
        ? '1px solid var(--nx-status-danger)'
        : '1px solid transparent',
    backgroundColor:
      variant === 'primary'
        ? 'var(--nx-action-primary)'
        : isDestructive
        ? 'var(--nx-status-danger)'
        : variant === 'secondary'
        ? 'var(--nx-surface-subtle)'
        : 'transparent',
    color: isActionSurface ? 'var(--nx-action-text)' : 'var(--nx-text-primary)',
    cursor: isDisabled ? 'not-allowed' : 'pointer',
    opacity: isDisabled ? 0.55 : 1,
    transition: 'background-color 0.15s ease, border-color 0.15s ease, opacity 0.15s ease',
    whiteSpace: 'nowrap',
    ...style,
  };

  return (
    <SurfaceProvider role={surfaceRole}>
      <button
        type={type}
        title={title}
        aria-label={ariaLabel}
        aria-busy={loading || undefined}
        style={buttonStyle}
        disabled={isDisabled}
        onClick={onClick}
        className={`nx-focusable ${className}`.trim()}
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
