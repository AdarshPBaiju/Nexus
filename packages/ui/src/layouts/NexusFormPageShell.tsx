import React from 'react';
import { NexusText } from '../typography/NexusText';

export interface NexusFormPageShellProps {
  readonly title: string;
  readonly description?: string;
  readonly submitAction?: React.ReactNode;
  readonly cancelAction?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusFormPageShell({
  title,
  description,
  submitAction,
  cancelAction,
  children,
}: NexusFormPageShellProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100dvh' }}>
      <header
        style={{
          padding: 'var(--nx-space-4) var(--nx-space-6)',
          borderBottom: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
        }}
      >
        <NexusText variant="h2">{title}</NexusText>
        {description && <NexusText role="secondary">{description}</NexusText>}
      </header>
      <main
        style={{
          flex: 1,
          maxWidth: '896px',
          width: '100%',
          margin: '0 auto',
          padding: 'var(--nx-space-6)',
        }}
      >
        {children}
      </main>
      {(submitAction || cancelAction) && (
        <footer
          style={{
            position: 'sticky',
            bottom: 0,
            padding: 'var(--nx-space-4) var(--nx-space-6)',
            backgroundColor: 'var(--nx-surface-card)',
            borderTop: '1px solid var(--nx-border-default)',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 'var(--nx-space-3)',
          }}
        >
          {cancelAction}
          {submitAction}
        </footer>
      )}
    </div>
  );
}
