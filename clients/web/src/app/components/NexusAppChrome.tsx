'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
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
        backgroundColor: 'var(--nx-surface-bg, #0a0e17)',
        color: 'var(--nx-text-primary, #f1f5f9)',
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '14px',
          padding: '32px',
        }}
      >
        <span
          aria-hidden="true"
          style={{
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            backgroundColor: 'var(--nx-action-primary, #2563eb)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.35)',
          }}
        >
          <NexusGlyph name="apps" size={24} color="var(--nx-action-text, #ffffff)" />
        </span>
        <span
          className="nx-numeric"
          style={{
            fontSize: '11px',
            fontWeight: 600,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            color: 'var(--nx-text-muted, #94a3b8)',
          }}
        >
          Restoring workstation session…
        </span>
        <span
          aria-hidden="true"
          className="nx-boot-progress"
          style={{
            width: '160px',
            height: '2px',
            borderRadius: '999px',
            overflow: 'hidden',
            backgroundColor: 'var(--nx-border-subtle, #26334d)',
          }}
        >
          <span
            style={{
              display: 'block',
              width: '45%',
              height: '100%',
              borderRadius: '999px',
              backgroundColor: 'var(--nx-accent-primary, #00f2fe)',
            }}
          />
        </span>
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
  const contentClass = `${
    isFlush
      ? 'nx-shell-content nx-shell-content--flush'
      : NARROW_ROUTES.includes(pathname)
      ? 'nx-shell-content nx-shell-content--narrow'
      : 'nx-shell-content'
  } nx-route`.trim();

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
        <div key={pathname} className={contentClass}>
          {children}
        </div>
      </main>
    </div>
  );
}
