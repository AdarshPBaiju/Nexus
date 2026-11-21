import React from 'react';
import { NexusCard } from '../surfaces/NexusCard';

export interface NexusAuthAndGuardShellProps {
  readonly children: React.ReactNode;
}

export function NexusAuthAndGuardShell({
  children,
}: NexusAuthAndGuardShellProps): React.JSX.Element {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100dvh',
        backgroundColor: 'var(--nx-surface-bg)',
        padding: 'var(--nx-space-4)',
      }}
    >
      <div style={{ maxWidth: '440px', width: '100%' }}>
        <NexusCard elevation="elevated">{children}</NexusCard>
      </div>
    </div>
  );
}
