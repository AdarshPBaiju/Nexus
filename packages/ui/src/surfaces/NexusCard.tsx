'use client';
import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';

export type CardElevation = 'flat' | 'card' | 'elevated' | 'subtle';

export interface NexusCardProps {
  readonly elevation?: CardElevation;
  readonly interactive?: boolean;
  readonly className?: string;
  readonly style?: React.CSSProperties;
  readonly children: React.ReactNode;
}

export function NexusCard({
  elevation = 'card',
  interactive = false,
  className = '',
  style = {},
  children,
}: NexusCardProps): React.JSX.Element {
  const surfaceRole: SurfaceRole = elevation === 'subtle' ? 'subtle' : elevation === 'elevated' ? 'elevated' : 'card';

  const cardStyle: React.CSSProperties = {
    position: 'relative',
    backgroundColor: `var(--nx-surface-${elevation === 'flat' ? 'subtle' : elevation})`,
    backgroundImage:
      'linear-gradient(180deg, color-mix(in srgb, var(--nx-surface-elevated) 42%, transparent) 0%, transparent 46%)',
    border: '1px solid var(--nx-border-default)',
    borderRadius: '12px',
    boxShadow: elevation === 'elevated' ? 'var(--nx-shadow-md)' : 'var(--nx-shadow-sm)',
    cursor: interactive ? 'pointer' : 'default',
    transition: 'border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease',
    ...style,
  };

  return (
    <SurfaceProvider role={surfaceRole}>
      <div
        style={cardStyle}
        className={`nx-card nx-card--${elevation} ${interactive ? 'nx-card--interactive' : ''} ${className}`.trim()}
      >
        {children}
      </div>
    </SurfaceProvider>
  );
}
