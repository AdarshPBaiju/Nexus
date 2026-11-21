import React from 'react';

export interface NexusSplitWorkspaceShellProps {
  readonly masterPane: React.ReactNode;
  readonly detailPane: React.ReactNode;
  readonly masterWidth?: string;
}

export function NexusSplitWorkspaceShell({
  masterPane,
  detailPane,
  masterWidth = '360px',
}: NexusSplitWorkspaceShellProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', height: '100dvh', overflow: 'hidden' }}>
      <aside
        style={{
          width: masterWidth,
          borderRight: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-subtle)',
          overflowY: 'auto',
        }}
      >
        {masterPane}
      </aside>
      <main style={{ flex: 1, backgroundColor: 'var(--nx-surface-bg)', overflowY: 'auto' }}>
        {detailPane}
      </main>
    </div>
  );
}
