import React from 'react';
import { NexusText } from '../typography/NexusText';
import { NexusIcon } from '../icons/NexusIcon';

export interface NexusCleanMainTopNavbarProps {
  readonly brandName?: string;
  readonly workspaceSwitcher?: React.ReactNode;
  readonly globalSearchTrigger?: React.ReactNode;
  readonly notificationBell?: React.ReactNode;
  readonly userAvatar?: React.ReactNode;
}

export function NexusCleanMainTopNavbar({
  brandName = 'PROJECT NEXUS',
  workspaceSwitcher,
  globalSearchTrigger,
  notificationBell,
  userAvatar,
}: NexusCleanMainTopNavbarProps): React.JSX.Element {
  return (
    <header
      style={{
        height: '56px',
        padding: '0 var(--nx-space-4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: 'var(--nx-surface-card)',
        borderBottom: '1px solid var(--nx-border-default)',
        userSelect: 'none',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
          <NexusIcon name="building" size="md" />
          <NexusText variant="h3">{brandName}</NexusText>
        </div>
        {workspaceSwitcher}
      </div>

      <div style={{ flex: 1, maxWidth: '480px', margin: '0 var(--nx-space-4)' }}>
        {globalSearchTrigger || (
          <div
            style={{
              height: '36px',
              backgroundColor: 'var(--nx-surface-subtle)',
              border: '1px solid var(--nx-border-default)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              padding: '0 var(--nx-space-3)',
              color: 'var(--nx-text-muted)',
              cursor: 'pointer',
              justifyContent: 'space-between',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
              <NexusIcon name="search" size="sm" />
              <NexusText variant="caption" role="muted">Quick search...</NexusText>
            </span>
            <span style={{ fontSize: '11px', padding: '2px 4px', border: '1px solid var(--nx-border-default)', borderRadius: '4px' }}>
              ⌘K
            </span>
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-3)' }}>
        {notificationBell}
        {userAvatar || (
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: 'var(--nx-surface-subtle)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <NexusIcon name="user" size="sm" />
          </div>
        )}
      </div>
    </header>
  );
}
