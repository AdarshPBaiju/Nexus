import React from 'react';
import { NexusText } from '../typography/NexusText';

export interface NexusDetailPageShellProps {
  readonly title: string;
  readonly statusBadge?: React.ReactNode;
  readonly metadataStrip?: React.ReactNode;
  readonly actions?: React.ReactNode;
  readonly tabs?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusDetailPageShell({
  title,
  statusBadge,
  metadataStrip,
  actions,
  tabs,
  children,
}: NexusDetailPageShellProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '100dvh' }}>
      <header
        style={{
          padding: 'var(--nx-space-4) var(--nx-space-6)',
          borderBottom: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-3)' }}>
            <NexusText variant="h2">{title}</NexusText>
            {statusBadge}
          </div>
          {actions && <div>{actions}</div>}
        </div>
        {metadataStrip && <div style={{ marginTop: 'var(--nx-space-2)' }}>{metadataStrip}</div>}
        {tabs && <div style={{ marginTop: 'var(--nx-space-3)' }}>{tabs}</div>}
      </header>
      <main style={{ flex: 1, padding: 'var(--nx-space-6)', overflow: 'auto' }}>
        {children}
      </main>
    </div>
  );
}
