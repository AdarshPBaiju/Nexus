'use client';

import React from 'react';
import { NexusBadge, NexusStack, NexusText } from '@nexus/ui';

export interface StudioInspectorProps {
  readonly payload: Record<string, unknown>;
  readonly previewState: string;
}

export function StudioInspector({ payload, previewState }: StudioInspectorProps): React.JSX.Element {
  return (
    <aside className="nx-inspector" aria-label="Live control inspector">
      <div
        style={{
          padding: '12px 14px',
          borderBottom: '1px solid var(--nx-border-subtle)',
          backgroundColor: 'var(--nx-surface-subtle)',
        }}
      >
        <NexusStack direction="row" align="center" justify="space-between">
          <NexusText variant="label">Live payload</NexusText>
          <NexusBadge variant="info" label={previewState.toUpperCase()} />
        </NexusStack>
        <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
          Typed values emitted by the controls on this page.
        </NexusText>
      </div>

      <div style={{ maxHeight: '336px', overflow: 'auto', padding: '10px 12px' }}>
        <pre
          style={{
            margin: 0,
            fontFamily: 'var(--font-mono)',
            fontSize: '10.5px',
            lineHeight: '16px',
            color: 'var(--nx-text-secondary)',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {JSON.stringify(payload, null, 2)}
        </pre>
      </div>

      <div
        style={{
          padding: '10px 14px 12px',
          borderTop: '1px solid var(--nx-border-subtle)',
          backgroundColor: 'var(--nx-surface-subtle)',
        }}
      >
        <NexusStack gap="6px">
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Token compliance</NexusText>
            <NexusBadge variant="success" dot label="Passing" />
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Contrast floor</NexusText>
            <NexusText variant="code" style={{ fontSize: '10.5px' }}>4.9:1 AA</NexusText>
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Target size</NexusText>
            <NexusText variant="code" style={{ fontSize: '10.5px' }}>≥ 38px</NexusText>
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Themes</NexusText>
            <NexusText variant="code" style={{ fontSize: '10.5px' }}>Dark · Light</NexusText>
          </NexusStack>
        </NexusStack>
      </div>
    </aside>
  );
}
