'use client';
import React from 'react';
import { SurfaceProvider, SurfaceRole } from '../theme/SurfaceContext';

export type CardElevation = 'flat' | 'card' | 'elevated' | 'subtle';

export interface NexusCardProps {
  readonly elevation?: CardElevation;
  readonly interactive?: boolean;
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function NexusCard({
  elevation = 'card',
  interactive = false,
  className = '',
  children,
}: NexusCardProps): React.JSX.Element {
  const surfaceRole: SurfaceRole = elevation === 'subtle' ? 'subtle' : elevation === 'elevated' ? 'elevated' : 'card';

  const cardStyle: React.CSSProperties = {
    backgroundColor: `var(--nx-surface-${elevation === 'flat' ? 'subtle' : elevation})`,
    border: '1px solid var(--nx-border-default)',
    borderRadius: '8px',
    cursor: interactive ? 'pointer' : 'default',
    transition: 'border-color 0.15s ease',
  };

  return (
    <SurfaceProvider role={surfaceRole}>
      <div style={cardStyle} className={className}>
        {children}
      </div>
    </SurfaceProvider>
  );
}
