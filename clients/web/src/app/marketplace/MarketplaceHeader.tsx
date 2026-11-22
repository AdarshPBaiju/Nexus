'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusSearchInput, NexusStack, NexusText } from '@nexus/ui';

export interface MarketplaceHeaderProps {
  readonly searchTerm: string;
  readonly onSearchChange: (val: string) => void;
  readonly installedCount: number;
  readonly totalCount: number;
}

export function MarketplaceHeader({
  searchTerm,
  onSearchChange,
  installedCount,
  totalCount,
}: MarketplaceHeaderProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '16px 20px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="14px">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
                Features & Ecosystem Marketplace
              </NexusText>
              <NexusBadge variant="success" label="Install = Enable (< 1ms)" />
              <NexusBadge variant="info" label="Zero Restart" />
            </div>
            <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
              Install, enable, and drain first-party café capabilities and third-party plugins in real time.
            </NexusText>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <NexusBox
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                backgroundColor: 'var(--nx-surface-subtle)',
                border: '1px solid var(--nx-border-subtle)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <NexusText variant="caption" role="muted">ACTIVE MODULES</NexusText>
              <NexusText variant="label" style={{ fontWeight: 700 }} className="nx-numeric">
                {installedCount} / {totalCount}
              </NexusText>
            </NexusBox>
          </div>
        </div>

        <div style={{ maxWidth: '420px' }}>
          <NexusSearchInput
            value={searchTerm}
            onChange={onSearchChange}
            placeholderKey="Search plugins by name, code, or keyword..."
            labelKey="Filter Catalog"
          />
        </div>
      </NexusStack>
    </NexusBox>
  );
}
