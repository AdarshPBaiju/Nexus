import React from 'react';
import { NexusText } from '../typography/NexusText';

export interface NexusOperationalCanvasShellProps {
  readonly stationTitle?: string;
  readonly cashierName?: string;
  readonly statusBarRight?: React.ReactNode;
  readonly statusBar?: React.ReactNode;
  readonly commandPalette?: React.ReactNode;
  readonly height?: string;
  readonly children: React.ReactNode;
}

export function NexusOperationalCanvasShell({
  stationTitle,
  cashierName,
  statusBarRight,
  statusBar,
  commandPalette,
  height = '100%',
  children,
}: NexusOperationalCanvasShellProps): React.JSX.Element {
  const hasStatusBar = Boolean(statusBar || stationTitle || cashierName || statusBarRight);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height,
        minHeight: 0,
        overflow: 'hidden',
        backgroundColor: 'var(--nx-surface-bg)',
      }}
    >
      {hasStatusBar && (
        <header
          style={{
            height: '44px',
            flexShrink: 0,
            backgroundColor: 'var(--nx-surface-card)',
            borderBottom: '1px solid var(--nx-border-default)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 'var(--nx-space-4)',
            padding: '0 var(--nx-space-4)',
          }}
        >
          {statusBar ?? (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--nx-space-3)',
                minWidth: 0,
              }}
            >
              <svg
                width={17}
                height={17}
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--nx-text-secondary)"
                strokeWidth={1.8}
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
                focusable="false"
                style={{ flexShrink: 0 }}
              >
                <path d="M4 10v10h16V10" />
                <path d="M3 10l2-6h14l2 6" />
                <path d="M3 10a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0" />
                <path d="M9 20v-5h6v5" />
              </svg>
              <NexusText variant="label" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {stationTitle}
              </NexusText>
              {cashierName && (
                <>
                  <span
                    aria-hidden="true"
                    style={{
                      width: '1px',
                      height: '14px',
                      backgroundColor: 'var(--nx-border-default)',
                    }}
                  />
                  <NexusText variant="caption" role="secondary" style={{ whiteSpace: 'nowrap' }}>
                    {cashierName}
                  </NexusText>
                </>
              )}
            </div>
          )}
          {statusBarRight && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
              {statusBarRight}
            </div>
          )}
        </header>
      )}
      <main style={{ flex: 1, minHeight: 0, position: 'relative', overflow: 'hidden' }}>
        {children}
      </main>
      {commandPalette}
    </div>
  );
}
