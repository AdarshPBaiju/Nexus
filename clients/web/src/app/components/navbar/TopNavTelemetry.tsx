'use client';

import React from 'react';
import { NexusText } from '@nexus/ui';

export function TopNavTelemetry(): React.JSX.Element {
  return (
    <span
      className="nx-topnav-latency"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        height: '26px',
        padding: '0 9px',
        borderRadius: '6px',
        border: '1px solid var(--nx-border-subtle)',
        backgroundColor: 'var(--nx-surface-subtle)',
      }}
      title="API round-trip latency (p99 budget 50ms)"
    >
      <span
        aria-hidden="true"
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '9999px',
          backgroundColor: 'var(--nx-status-success)',
        }}
      />
      <NexusText variant="code" role="muted" style={{ fontSize: '10px' }}>
        43ms · p99 &lt; 50ms
      </NexusText>
    </span>
  );
}
