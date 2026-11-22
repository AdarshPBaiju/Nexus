'use client';

import React from 'react';
import { NexusBox, NexusStack, NexusText } from '@nexus/ui';

export interface QuotaItem {
  readonly label: string;
  readonly value: string;
  readonly percentage: number;
  readonly colorToken: string;
}

export function BillingQuotaMeters(): React.JSX.Element {
  const quotas: readonly QuotaItem[] = [
    { label: 'POS Workstations', value: '3 / 10 Active', percentage: 30, colorToken: 'var(--nx-action-primary)' },
    { label: 'Daily Orders Quota', value: '1,420 / 10,000 Today', percentage: 14.2, colorToken: 'var(--nx-status-success)' },
    { label: 'Kitchen KDS Displays', value: '2 / 5 Screens', percentage: 40, colorToken: 'var(--nx-status-warning)' },
    { label: 'MinIO S3 WORM Storage', value: '42.4 MB / 100 GB', percentage: 0.1, colorToken: 'var(--nx-accent-cyan, #0284C7)' },
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        padding: '16px',
        borderRadius: '10px',
        backgroundColor: 'var(--nx-surface-subtle)',
        border: '1px solid var(--nx-border-subtle)',
      }}
    >
      {quotas.map((q) => (
        <NexusBox key={q.label}>
          <NexusStack gap="4px">
            <NexusText variant="caption" role="muted" style={{ textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.04em' }}>
              {q.label}
            </NexusText>
            <NexusText variant="label" style={{ fontWeight: 700, fontFamily: 'var(--font-mono, monospace)' }}>
              {q.value}
            </NexusText>
            <div
              style={{
                width: '100%',
                height: '6px',
                borderRadius: '3px',
                backgroundColor: 'var(--nx-border-default)',
                overflow: 'hidden',
                marginTop: '4px',
              }}
            >
              <div
                style={{
                  width: `${Math.max(q.percentage, 4)}%`,
                  height: '100%',
                  borderRadius: '3px',
                  backgroundColor: q.colorToken,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </NexusStack>
        </NexusBox>
      ))}
    </div>
  );
}
