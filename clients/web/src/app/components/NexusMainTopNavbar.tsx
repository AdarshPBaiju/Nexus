'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  NexusBadge,
  NexusBox,
  NexusButton,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { useAuth } from '../../runtime/auth/AuthContext';

export interface NexusMainTopNavbarProps {
  readonly onToggleSidebar?: () => void;
  readonly isSidebarOpen?: boolean;
}

export function NexusMainTopNavbar({
  onToggleSidebar,
  isSidebarOpen = true,
}: NexusMainTopNavbarProps): React.JSX.Element {
  const { session } = useAuth();
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isLocked, setIsLocked] = useState(false);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
    document.documentElement.className = nextTheme;
  };

  return (
    <NexusBox
      padding="0 var(--nx-space-4)"
      style={{
        height: '56px',
        backgroundColor: 'var(--nx-surface-card)',
        borderBottom: '1px solid var(--nx-border-default)',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}
    >
      {/* Left: Mobile/Sidebar trigger + Brand Logo + Tenant & Scope */}
      <NexusStack direction="row" align="center" gap="var(--nx-space-3)">
        <NexusButton variant="ghost" size="sm" onClick={onToggleSidebar}>
          <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>
            {isSidebarOpen ? 'menu_open' : 'menu'}
          </span>
        </NexusButton>

        <Link href="/">
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <NexusText variant="h3" style={{ letterSpacing: '-0.5px', fontWeight: 800 }}>
              NEXUS
            </NexusText>
            <NexusBadge variant="neutral" label="v5.4 PRO" />
          </NexusStack>
        </Link>

        {/* 6-Dim Org Scope Pill */}
        <NexusBox
          padding="4px 10px"
          style={{
            backgroundColor: 'var(--nx-surface-subtle)',
            borderRadius: '6px',
            border: '1px solid var(--nx-border-subtle)',
          }}
        >
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <span className="material-symbols-outlined" style={{ fontSize: '14px', color: 'var(--nx-text-secondary)' }}>
              storefront
            </span>
            <NexusText variant="caption" role="primary">
              {session.tenantName}
            </NexusText>
            <NexusText variant="caption" role="muted">
              · {session.branchName}
            </NexusText>
          </NexusStack>
        </NexusBox>
      </NexusStack>

      {/* Center: Global Command Palette Search */}
      <NexusBox style={{ flex: 1, maxWidth: '420px', margin: '0 var(--nx-space-4)' }}>
        <NexusBox
          padding="6px 12px"
          style={{
            backgroundColor: 'var(--nx-surface-subtle)',
            borderRadius: '6px',
            border: '1px solid var(--nx-border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
          }}
        >
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <span className="material-symbols-outlined" style={{ fontSize: '16px', color: 'var(--nx-text-muted)' }}>
              search
            </span>
            <NexusText variant="caption" role="muted">
              Quick navigate, scan SKU, or command...
            </NexusText>
          </NexusStack>
          <NexusText variant="code" role="muted" style={{ fontSize: '10px', padding: '1px 4px', backgroundColor: 'var(--nx-surface-card)', borderRadius: '3px' }}>
            ⌘K
          </NexusText>
        </NexusBox>
      </NexusBox>

      {/* Right: Runtime Status + Theme + Cashier PIN Lock */}
      <NexusStack direction="row" align="center" gap="var(--nx-space-3)">
        {/* Runtime Status */}
        <NexusStack direction="row" align="center" gap="var(--nx-space-1)">
          <NexusBadge variant="success" label="API:8000" />
          <NexusBadge variant="neutral" label="DESKTOP:OK" />
        </NexusStack>

        {/* Theme Toggle */}
        <NexusButton variant="outline" size="sm" onClick={toggleTheme}>
          <span className="material-symbols-outlined" style={{ fontSize: '16px' }}>
            {theme === 'dark' ? 'light_mode' : 'dark_mode'}
          </span>
        </NexusButton>

        {/* Cashier User & Lock */}
        <NexusButton
          variant={isLocked ? 'destructive' : 'secondary'}
          size="sm"
          onClick={() => setIsLocked(!isLocked)}
        >
          <NexusStack direction="row" align="center" gap="var(--nx-space-1)">
            <span className="material-symbols-outlined" style={{ fontSize: '14px' }}>
              {isLocked ? 'lock' : 'lock_open'}
            </span>
            <NexusText variant="caption">
              {isLocked ? 'LOCKED' : session.name}
            </NexusText>
          </NexusStack>
        </NexusButton>
      </NexusStack>
    </NexusBox>
  );
}
