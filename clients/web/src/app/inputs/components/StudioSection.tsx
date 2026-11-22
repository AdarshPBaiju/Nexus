'use client';

import React from 'react';
import { NexusBadge, NexusCard, NexusStack, NexusText } from '@nexus/ui';

export interface StudioSectionProps {
  readonly index: string;
  readonly title: string;
  readonly description: string;
  readonly badge?: string;
  readonly children: React.ReactNode;
}

export function StudioSection({
  index,
  title,
  description,
  badge,
  children,
}: StudioSectionProps): React.JSX.Element {
  return (
    <NexusCard elevation="card" style={{ padding: '16px' }}>
      <NexusStack gap="12px">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', minWidth: 0 }}>
            <span
              aria-hidden="true"
              style={{
                flexShrink: 0,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '24px',
                height: '24px',
                borderRadius: '6px',
                backgroundColor: 'var(--nx-surface-subtle)',
                border: '1px solid var(--nx-border-subtle)',
                color: 'var(--nx-text-secondary)',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              {index}
            </span>
            <div style={{ minWidth: 0 }}>
              <NexusText variant="h4">{title}</NexusText>
              <NexusText variant="caption" role="muted" style={{ display: 'block' }}>
                {description}
              </NexusText>
            </div>
          </div>
          {badge && <NexusBadge variant="neutral" label={badge} />}
        </div>
        <div className="nx-studio-fields">{children}</div>
      </NexusStack>
    </NexusCard>
  );
}
