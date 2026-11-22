'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph } from './NexusGlyph';
import { useAuth } from '../../runtime/auth/AuthContext';
import { TopNavSearch } from './navbar/TopNavSearch';
import { TopNavTelemetry } from './navbar/TopNavTelemetry';
import { TopNavOperator } from './navbar/TopNavOperator';
import { TopNavScopePicker } from './navbar/TopNavScopePicker';

export interface NexusMainTopNavbarProps {
  readonly onToggleSidebar?: () => void;
  readonly isSidebarOpen?: boolean;
}

type ThemeMode = 'dark' | 'light';

const THEME_STORAGE_KEY = 'nexus.theme';

function readStoredTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'dark';
  try {
    const stored = window.sessionStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {
    // Ignore restricted storage contexts.
  }
  return 'dark';
}

export function NexusMainTopNavbar({
  onToggleSidebar,
  isSidebarOpen = true,
}: NexusMainTopNavbarProps): React.JSX.Element {
  const { session, activeStaff, lockWorkstation } = useAuth();
  const [theme, setTheme] = useState<ThemeMode>('dark');

  useEffect(() => {
    const stored = readStoredTheme();
    setTheme(stored);
    document.documentElement.setAttribute('data-theme', stored);
  }, []);

  const toggleTheme = useCallback(() => {
    const nextTheme: ThemeMode = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
    try {
      window.sessionStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    } catch {
      // Theme stays in memory when storage is unavailable.
    }
  }, [theme]);

  return (
    <header
      className="nx-topnav"
      style={{
        height: '56px',
        borderBottom: '1px solid var(--nx-border-default)',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--nx-space-3)',
        padding: '0 12px',
      }}
    >
      <NexusStack direction="row" align="center" gap="var(--nx-space-3)" style={{ minWidth: 0 }}>
        <NexusButton
          variant="ghost"
          size="sm"
          onClick={onToggleSidebar}
          ariaLabel={isSidebarOpen ? 'Collapse navigation' : 'Expand navigation'}
          title={isSidebarOpen ? 'Collapse navigation' : 'Expand navigation'}
        >
          <NexusGlyph name={isSidebarOpen ? 'menu_open' : 'menu'} size={19} />
        </NexusButton>

        <Link href="/" style={{ textDecoration: 'none' }}>
          <NexusStack direction="row" align="center" gap="8px">
            <NexusBox
              className="nx-brand-mark"
              style={{
                width: '28px',
                height: '28px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'var(--nx-action-primary)',
              }}
            >
              <NexusGlyph name="apps" size={17} color="var(--nx-action-text)" />
            </NexusBox>
            <NexusText variant="h4" style={{ letterSpacing: '-0.02em' }}>
              NEXUS
            </NexusText>
            <NexusBadge variant="neutral" label="v5.4 PRO" />
          </NexusStack>
        </Link>

        <TopNavScopePicker />
      </NexusStack>

      <TopNavSearch />

      <NexusStack direction="row" align="center" gap="8px" style={{ flexShrink: 0 }}>
        <TopNavTelemetry />

        <NexusButton
          variant="outline"
          size="sm"
          onClick={toggleTheme}
          ariaLabel={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          <NexusGlyph name={theme === 'dark' ? 'light_mode' : 'dark_mode'} size={16} />
        </NexusButton>

        <TopNavOperator
          session={session}
          activeStaff={activeStaff}
          onLock={lockWorkstation}
        />
      </NexusStack>
    </header>
  );
}
