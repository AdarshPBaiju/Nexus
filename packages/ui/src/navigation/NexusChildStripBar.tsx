import React from 'react';
import { NavItem } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusChildStripBarProps {
  readonly topItems: readonly NavItem[];
  readonly childItems?: readonly NavItem[];
  readonly activeTopId?: string;
  readonly onSelectTop?: (id: string) => void;
}

export function NexusChildStripBar({
  topItems,
  childItems = [],
  activeTopId,
  onSelectTop,
}: NexusChildStripBarProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', width: '100%', borderBottom: '1px solid var(--nx-border-default)' }}>
      {/* Top Primary Navigation Strip */}
      <nav
        style={{
          height: '44px',
          backgroundColor: 'var(--nx-surface-subtle)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 var(--nx-space-4)',
          gap: 'var(--nx-space-4)',
        }}
        aria-label="Below-Navbar Top Strip"
      >
        {topItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelectTop?.(item.id)}
            style={{
              background: 'transparent',
              border: 'none',
              padding: '4px 8px',
              cursor: 'pointer',
              borderBottom: item.id === activeTopId ? '2px solid var(--nx-action-primary)' : 'none',
            }}
          >
            <NexusText variant="label">{item.label}</NexusText>
          </button>
        ))}
      </nav>

      {/* Child Context Strip (only rendered if child items exist) */}
      {childItems.length > 0 && (
        <div
          style={{
            height: '36px',
            backgroundColor: 'var(--nx-surface-card)',
            display: 'flex',
            alignItems: 'center',
            padding: '0 var(--nx-space-4)',
            gap: 'var(--nx-space-3)',
            borderTop: '1px solid var(--nx-border-subtle)',
          }}
        >
          {childItems.map((child) => (
            <span key={child.id} style={{ cursor: 'pointer' }}>
              <NexusText variant="caption">{child.label}</NexusText>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
