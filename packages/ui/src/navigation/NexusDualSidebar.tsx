import React from 'react';
import { NavItem } from './types';
import { NexusText } from '../typography/NexusText';
import { NexusIcon } from '../icons/NexusIcon';

export interface NexusDualSidebarProps {
  readonly primaryItems: readonly NavItem[];
  readonly secondaryItems: readonly NavItem[];
  readonly activePrimaryId?: string;
  readonly onSelectPrimary?: (id: string) => void;
}

export function NexusDualSidebar({
  primaryItems,
  secondaryItems,
  activePrimaryId,
  onSelectPrimary,
}: NexusDualSidebarProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* Primary Rail */}
      <nav
        style={{
          width: '64px',
          backgroundColor: 'var(--nx-surface-subtle)',
          borderInlineEnd: '1px solid var(--nx-border-default)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: 'var(--nx-space-2) 0',
          gap: 'var(--nx-space-2)',
        }}
        aria-label="Primary Navigation Rail"
      >
        {primaryItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelectPrimary?.(item.id)}
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: item.id === activePrimaryId ? 'var(--nx-surface-selected)' : 'transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title={item.label}
          >
            <NexusIcon name="building" size="md" />
          </button>
        ))}
      </nav>

      {/* Secondary Drawer */}
      <aside
        style={{
          width: '200px',
          backgroundColor: 'var(--nx-surface-card)',
          borderInlineEnd: '1px solid var(--nx-border-default)',
          padding: 'var(--nx-space-3)',
          overflowY: 'auto',
        }}
        aria-label="Secondary Navigation Pane"
      >
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {secondaryItems.map((item) => (
            <li key={item.id} style={{ padding: '6px 8px', borderRadius: '4px', cursor: 'pointer' }}>
              <NexusText variant="body">{item.label}</NexusText>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
