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
  readonly style?: React.CSSProperties;
  readonly title?: string;
  readonly children: React.ReactNode;
}

const VARIANT_ELEMENT: Record<TextVariant, keyof React.JSX.IntrinsicElements> = {
  h1: 'h1',
  h2: 'h2',
  h3: 'h3',
  h4: 'h4',
  body: 'p',
  caption: 'span',
  code: 'code',
  label: 'span',
  kpi: 'span',
};

function resolveColor(surface: string, role: TextColorRole): string {
  if (surface === 'primary-action' || surface === 'destructive-action') {
    return 'var(--nx-action-text)';
  }
  if (surface === 'tooltip') {
    return 'var(--nx-text-inverse)';
  }
  if (surface === 'status-success-subtle') {
    return 'var(--nx-status-success-text)';
  }
  if (surface === 'status-warning-subtle') {
    return 'var(--nx-status-warning-text)';
  }
  if (surface === 'status-danger-subtle') {
    return 'var(--nx-status-danger-text)';
  }
  if (surface === 'status-info-subtle') {
    return 'var(--nx-status-info-text)';
  }
  if (role === 'secondary') {
    return 'var(--nx-text-secondary)';
  }
  if (role === 'muted') {
    return 'var(--nx-text-muted)';
  }
  if (role === 'disabled') {
    return 'var(--nx-text-disabled)';
  }
  return 'var(--nx-text-primary)';
}

export function NexusText({
  variant = 'body',
  role = 'primary',
  tabular = false,
  className = '',
  style = {},
  title,
  children,
}: NexusTextProps): React.JSX.Element {
  const surface = useSurface();
  const Component = VARIANT_ELEMENT[variant];

  const textStyle: React.CSSProperties = {
    color: resolveColor(surface, role),
    ...style,
  };

  return React.createElement(
    Component,
    {
      className: `nx-text nx-text--${variant} ${tabular ? 'nx-numeric' : ''} ${className}`.trim(),
      style: textStyle,
      title,
    },
    children
  );
}
