import React from 'react';

export interface NexusOperationalCanvasShellProps {
  readonly statusBar?: React.ReactNode;
  readonly commandPalette?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusOperationalCanvasShell({
  statusBar,
  commandPalette,
  children,
}: NexusOperationalCanvasShellProps): React.JSX.Element {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100dvh',
        overflow: 'hidden',
        backgroundColor: 'var(--nx-surface-bg)',
        userSelect: 'none',
      }}
    >
      {statusBar && (
        <header
          style={{
            height: '44px',
            backgroundColor: 'var(--nx-surface-card)',
            borderBottom: '1px solid var(--nx-border-default)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 var(--nx-space-4)',
          }}
        >
          {statusBar}
        </header>
      )}
      <main style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {children}
      </main>
      {commandPalette}
    </div>
  );
}
