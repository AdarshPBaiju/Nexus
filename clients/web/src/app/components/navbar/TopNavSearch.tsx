'use client';

import React from 'react';
import { NexusText } from '@nexus/ui';
import { NexusGlyph } from '../NexusGlyph';

export function TopNavSearch(): React.JSX.Element {
  return (
    <button
      type="button"
      className="nx-topnav-search nx-focusable"
      style={{
        flex: 1,
        maxWidth: '400px',
        height: '30px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '8px',
        padding: '0 10px',
        borderRadius: '6px',
        border: '1px solid var(--nx-border-subtle)',
        backgroundColor: 'var(--nx-surface-subtle)',
        cursor: 'pointer',
      }}
      aria-label="Open command palette"
    >
      <span style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
        <NexusGlyph name="search" size={16} color="var(--nx-text-muted)" />
        <NexusText variant="caption" role="muted">
          Search orders, SKUs, or run a command
        </NexusText>
      </span>
      <NexusText
        variant="code"
        role="muted"
        style={{
          fontSize: '10px',
          padding: '1px 5px',
          borderRadius: '4px',
          border: '1px solid var(--nx-border-subtle)',
        }}
      >
        ⌘K
      </NexusText>
    </button>
  );
}
