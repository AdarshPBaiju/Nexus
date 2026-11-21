import React from 'react';
import { NexusText } from '../typography/NexusText';

export interface NexusDashboardPageShellProps {
  readonly title: string;
  readonly periodSelector?: React.ReactNode;
  readonly actions?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusDashboardPageShell({
  title,
  periodSelector,
  actions,
  children,
}: NexusDashboardPageShellProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100dvh' }}>
      <header
        style={{
          height: '56px',
          padding: '0 var(--nx-space-6)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
        }}
      >
        <NexusText variant="h2">{title}</NexusText>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-3)' }}>
          {periodSelector}
          {actions}
        </div>
      </header>
      <main style={{ flex: 1, padding: 'var(--nx-space-6)', overflow: 'auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 'var(--nx-space-4)' }}>
          {children}
        </div>
      </main>
    </div>
  );
}
