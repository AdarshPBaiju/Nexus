import React from 'react';
import { NavigationModeController } from './NavigationModeController';
import { NavItem } from './types';
import { NexusCleanMainTopNavbar } from './NexusCleanMainTopNavbar';
import { NexusNestedSidebar } from './NexusNestedSidebar';
import { NexusChildStripBar } from './NexusChildStripBar';
import { NexusOperationalMinimalBar } from './NexusOperationalMinimalBar';

export interface NexusAppLayoutShellProps {
  readonly navigationController: NavigationModeController;
  readonly navItems: readonly NavItem[];
  readonly activeNavId?: string;
  readonly dir?: 'ltr' | 'rtl';
  readonly children: React.ReactNode;
}

export function NexusAppLayoutShell({
  navigationController,
  navItems,
  activeNavId,
  dir = 'ltr',
  children,
}: NexusAppLayoutShellProps): React.JSX.Element {
  const mode = navigationController.mode;

  return (
    <div
      dir={dir}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100dvh',
        overflow: 'hidden',
        backgroundColor: 'var(--nx-surface-bg)',
      }}
    >
      {/* 56px Clean Top Navbar (zero nav links) */}
      {mode !== 'OPERATIONAL_MINIMAL' && <NexusCleanMainTopNavbar />}

      {/* Mode E: Operational minimal bar */}
      {mode === 'OPERATIONAL_MINIMAL' && (
        <NexusOperationalMinimalBar stationName="POS-01" cashierName="Staff Cashier" />
      )}

      {/* Mode C: Below-nav top strip */}
      {mode === 'TOP_CHILD_STRIP' && (
        <NexusChildStripBar topItems={navItems} activeTopId={activeNavId} />
      )}

      {/* Main Layout Container with Nested Sidebar for Mode A */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {(mode === 'NESTED_SIDEBAR' || mode === 'DUAL_SIDEBAR') && (
          <NexusNestedSidebar
            items={navItems}
            activeId={activeNavId}
            isCollapsed={navigationController.isCollapsed}
          />
        )}
        <main style={{ flex: 1, overflowY: 'auto' }}>{children}</main>
      </div>
    </div>
  );
}
