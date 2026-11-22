'use client';
import React from 'react';
import { useSurface } from '../theme/SurfaceContext';

export type TextVariant =
  | 'h1'
  | 'h2'
  | 'h3'
  | 'h4'
  | 'body'
  | 'caption'
  | 'code'
  | 'label'
  | 'kpi';

export type TextColorRole = 'primary' | 'secondary' | 'muted' | 'disabled';

export interface NexusTextProps {
  readonly variant?: TextVariant;
  readonly role?: TextColorRole;
  readonly tabular?: boolean;
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function NexusText({
  variant = 'body',
  role = 'primary',
  tabular = false,
  className = '',
  children,
}: NexusTextProps): React.JSX.Element {
  const surface = useSurface();

  // Background-Aware Token Resolution
  let colorVar = 'var(--nx-text-primary)';
  if (surface === 'primary-action' || surface === 'destructive-action') {
    colorVar = 'var(--nx-action-text)';
  } else if (surface === 'tooltip') {
    colorVar = 'var(--nx-text-inverse)';
  } else if (surface === 'status-success-subtle') {
    colorVar = 'var(--nx-status-success-text)';
  } else if (surface === 'status-warning-subtle') {
    colorVar = 'var(--nx-status-warning-text)';
  } else if (surface === 'status-danger-subtle') {
    colorVar = 'var(--nx-status-danger-text)';
  } else if (surface === 'status-info-subtle') {
    colorVar = 'var(--nx-status-info-text)';
  } else if (role === 'secondary') {
    colorVar = 'var(--nx-text-secondary)';
  } else if (role === 'muted') {
    colorVar = 'var(--nx-text-muted)';
  } else if (role === 'disabled') {
    colorVar = 'var(--nx-text-disabled)';
  }

  const baseStyle: React.CSSProperties = {
    color: colorVar,
    fontVariantNumeric: tabular ? 'tabular-nums lining-nums' : undefined,
    textAlign: tabular ? 'end' : undefined,
  };

  const Component = variant.startsWith('h') ? (variant as keyof React.JSX.IntrinsicElements) : 'span';
  return (
    <Component style={baseStyle} className={className}>
      {children}
    </Component>
  );
}
