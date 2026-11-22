import React from 'react';
import { NexusText } from '../typography/NexusText';

export interface NexusDetailPageShellProps {
  readonly title: string;
  readonly subtitle?: string;
  readonly statusBadge?: React.ReactNode;
  readonly metadataStrip?: React.ReactNode;
  readonly actions?: React.ReactNode;
  readonly headerActions?: React.ReactNode;
  readonly tabs?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusDetailPageShell({
  title,
  subtitle,
  statusBadge,
  metadataStrip,
  actions,
  headerActions,
  tabs,
  children,
}: NexusDetailPageShellProps): React.JSX.Element {
  const resolvedActions = actions ?? headerActions;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '100dvh' }}>
      <header
        style={{
          padding: 'var(--nx-space-4) var(--nx-space-6)',
          borderBottom: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 'var(--nx-space-4)' }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-3)' }}>
              <NexusText variant="h2">{title}</NexusText>
              {statusBadge}
            </div>
            {subtitle && (
              <NexusText variant="body" role="secondary" style={{ marginTop: '2px' }}>
                {subtitle}
              </NexusText>
            )}
          </div>
          {resolvedActions && <div>{resolvedActions}</div>}
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
