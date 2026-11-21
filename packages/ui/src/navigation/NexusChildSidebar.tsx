import React from 'react';
import { NavItem } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusChildSidebarProps {
  readonly topItems: readonly NavItem[];
  readonly childItems?: readonly NavItem[];
  readonly activeTopId?: string;
  readonly onSelectTop?: (id: string) => void;
  readonly children: React.ReactNode;
}

export function NexusChildSidebar({
  topItems,
  childItems = [],
  activeTopId,
  onSelectTop,
  children,
}: NexusChildSidebarProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Below-Nav Top Strip */}
      <nav
        style={{
          height: '44px',
          backgroundColor: 'var(--nx-surface-subtle)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 var(--nx-space-4)',
          gap: 'var(--nx-space-4)',
          borderBottom: '1px solid var(--nx-border-default)',
        }}
      >
        {topItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelectTop?.(item.id)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              borderBottom: item.id === activeTopId ? '2px solid var(--nx-action-primary)' : 'none',
            }}
          >
            <NexusText variant="label">{item.label}</NexusText>
          </button>
        ))}
      </nav>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Child Context Sidebar (auto-collapses to 0 width if empty) */}
        {childItems.length > 0 && (
          <aside
            style={{
              width: '220px',
              backgroundColor: 'var(--nx-surface-card)',
              borderInlineEnd: '1px solid var(--nx-border-default)',
              padding: 'var(--nx-space-3)',
              overflowY: 'auto',
            }}
          >
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {childItems.map((child) => (
                <li key={child.id} style={{ padding: '6px 8px', cursor: 'pointer' }}>
                  <NexusText variant="body">{child.label}</NexusText>
                </li>
              ))}
            </ul>
          </aside>
        )}
        <main style={{ flex: 1, overflowY: 'auto' }}>{children}</main>
      </div>
    </div>
  );
}
