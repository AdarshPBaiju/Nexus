'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { NexusText } from '@nexus/ui';
import { useAuth } from '../../runtime/auth/AuthContext';
import { CashierPinLoginScreen } from './CashierPinLoginScreen';
import { NexusEnterpriseSidebar } from './NexusEnterpriseSidebar';
import { NexusMainTopNavbar } from './NexusMainTopNavbar';
import { NexusGlyph } from './NexusGlyph';

const FLUSH_ROUTES: readonly string[] = ['/pos', '/kitchen'];
const NARROW_ROUTES: readonly string[] = ['/onboarding'];

export interface NexusAppChromeProps {
  readonly children: React.ReactNode;
}

function BootScreen(): React.JSX.Element {
  return (
    <div
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--nx-surface-bg)',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 'var(--nx-space-3)',
          padding: 'var(--nx-space-6)',
        }}
      >
        <span
          aria-hidden="true"
          style={{
            width: '34px',
            height: '34px',
            borderRadius: '10px',
            backgroundColor: 'var(--nx-action-primary)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <NexusGlyph name="apps" size={21} color="var(--nx-action-text)" />
        </span>
        <NexusText variant="label" role="secondary">
          Restoring workstation session…
        </NexusText>
      </div>
    </div>
  );
}

export function NexusAppChrome({ children }: NexusAppChromeProps): React.JSX.Element {
  const pathname = usePathname();
  const { isAuthenticated, isHydrated } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const query = window.matchMedia('(max-width: 1100px)');
    if (query.matches) {
      setIsSidebarOpen(false);
    }
  }, []);

  if (!isHydrated) {
    return <BootScreen />;
  }

  if (!isAuthenticated) {
    return <CashierPinLoginScreen />;
  }

  const isFlush = FLUSH_ROUTES.includes(pathname);
  const contentClass = isFlush
    ? 'nx-shell-content nx-shell-content--flush'
    : NARROW_ROUTES.includes(pathname)
    ? 'nx-shell-content nx-shell-content--narrow'
    : 'nx-shell-content';

  return (
    <div className="nx-shell">
      <NexusMainTopNavbar
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={() => setIsSidebarOpen((open) => !open)}
      />

      {isSidebarOpen && (
        <button
          type="button"
          className="nx-sidebar-scrim"
          aria-label="Close navigation"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <NexusEnterpriseSidebar
        isOpen={isSidebarOpen}
        onNavigate={() => {
          if (typeof window !== 'undefined' && window.matchMedia('(max-width: 1100px)').matches) {
            setIsSidebarOpen(false);
          }
        }}
      />

      <main className={`nx-shell-main ${isSidebarOpen ? '' : 'nx-shell-main--collapsed'}`.trim()}>
        <div className={contentClass}>{children}</div>
      </main>
    </div>
  );
}
