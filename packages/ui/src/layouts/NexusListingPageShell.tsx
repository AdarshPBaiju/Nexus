import React from 'react';
import { NexusText } from '../typography/NexusText';
import { NexusBadge } from '../surfaces/NexusBadge';

export interface NexusListingPageShellProps {
  readonly title: string;
  readonly subtitle?: string;
  readonly recordCount?: number;
  readonly actions?: React.ReactNode;
  readonly primaryAction?: React.ReactNode;
  readonly searchBar?: React.ReactNode;
  readonly filterPresets?: React.ReactNode;
  readonly children: React.ReactNode;
}

export function NexusListingPageShell({
  title,
  subtitle,
  recordCount,
  actions,
  primaryAction,
  searchBar,
  filterPresets,
  children,
}: NexusListingPageShellProps): React.JSX.Element {
  const resolvedActions = actions ?? primaryAction;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: '100dvh' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-3)' }}>
          <NexusText variant="h2">{title}</NexusText>
          {recordCount !== undefined && (
            <NexusBadge label={recordCount.toString()} variant="neutral" />
          )}
          {subtitle && (
            <NexusText variant="caption" role="secondary">
              {subtitle}
            </NexusText>
          )}
        </div>
        {resolvedActions && <div>{resolvedActions}</div>}
      </header>
      {(searchBar || filterPresets) && (
        <div
          style={{
            padding: 'var(--nx-space-3) var(--nx-space-6)',
            display: 'flex',
            gap: 'var(--nx-space-4)',
            borderBottom: '1px solid var(--nx-border-subtle)',
            backgroundColor: 'var(--nx-surface-subtle)',
          }}
        >
          {searchBar}
          {filterPresets}
        </div>
      )}
      <main style={{ flex: 1, padding: 'var(--nx-space-6)', overflow: 'auto' }}>
        {children}
      </main>
    </div>
  );
}
