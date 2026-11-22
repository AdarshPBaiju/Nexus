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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      <header
        style={{
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          border: '1px solid var(--nx-border-default)',
          borderRadius: '12px',
          backgroundColor: 'var(--nx-surface-card)',
          backgroundImage: 'linear-gradient(180deg, color-mix(in srgb, var(--nx-surface-elevated) 40%, transparent), transparent 60%)',
          boxShadow: 'var(--nx-shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minWidth: 0, flex: '1 1 220px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)', flexWrap: 'wrap' }}>
            <NexusText variant="h2">{title}</NexusText>
            {recordCount !== undefined && (
              <NexusBadge label={recordCount.toString()} variant="neutral" />
            )}
          </div>
          {subtitle && (
            <NexusText variant="caption" role="secondary">
              {subtitle}
            </NexusText>
          )}
        </div>
        {resolvedActions && <div style={{ flexShrink: 0 }}>{resolvedActions}</div>}
      </header>
      {(searchBar || filterPresets) && (
        <div
          style={{
            marginTop: '12px',
            padding: '8px 10px',
            display: 'flex',
            gap: 'var(--nx-space-4)',
            border: '1px solid var(--nx-border-default)',
            borderRadius: '10px',
            backgroundColor: 'var(--nx-surface-card)',
            boxShadow: 'var(--nx-shadow-xs)',
          }}
        >
          {searchBar}
          {filterPresets}
        </div>
      )}
      <main style={{ flex: 1, padding: 'var(--nx-space-5) 0 0', overflow: 'visible' }}>
        {children}
      </main>
    </div>
  );
}
