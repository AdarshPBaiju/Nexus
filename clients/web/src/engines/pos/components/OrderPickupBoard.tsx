'use client';

import React from 'react';
import type { OrderPickupTokenDto } from '../catalog.types';

export interface OrderPickupBoardProps {
  readonly tokens: readonly OrderPickupTokenDto[];
  readonly venueTitle?: string;
}

export const OrderPickupBoard: React.FC<OrderPickupBoardProps> = ({
  tokens,
  venueTitle = 'Café Pickup Status',
}) => {
  const preparingTokens = tokens.filter((t) => t.status === 'PREPARING');
  const readyTokens = tokens.filter((t) => t.status === 'READY');

  return (
    <div className="w-full h-full min-h-screen bg-[var(--nx-surface-bg)] text-[var(--nx-text-primary)] p-6 flex flex-col font-sans select-none">
      <header className="border-b border-[var(--nx-border-subtle)] pb-4 mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--nx-text-primary)]">
            {venueTitle}
          </h1>
          <p className="text-sm text-[var(--nx-text-secondary)]">
            Please watch for your order token
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[var(--nx-status-success)] animate-pulse" />
          <span className="text-xs font-semibold text-[var(--nx-text-muted)] tracking-wider uppercase">
            Live Updates
          </span>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-2 gap-8">
        {/* Preparing Column */}
        <section aria-labelledby="preparing-heading" className="flex flex-col rounded-3xl bg-[var(--nx-surface-card)] border border-[var(--nx-border-default)] p-6 shadow-sm">
          <div className="border-b border-[var(--nx-border-subtle)] pb-3 mb-6 flex justify-between items-center">
            <h2 id="preparing-heading" className="text-lg font-bold tracking-wider text-[var(--nx-status-warning-text)] uppercase">
              Preparing ({preparingTokens.length})
            </h2>
            <span className="text-xs px-2.5 py-1 rounded-full bg-[var(--nx-status-warning-subtle)] text-[var(--nx-status-warning-text)] font-semibold">
              In Kitchen
            </span>
          </div>

          <div className="flex-1 overflow-y-auto grid grid-cols-3 gap-4 auto-rows-max">
            {preparingTokens.map((t) => (
              <div
                key={t.token}
                className="min-h-[72px] rounded-2xl bg-[var(--nx-surface-subtle)] border border-[var(--nx-border-subtle)] flex flex-col items-center justify-center p-3 text-center"
              >
                <span className="text-3xl font-extrabold tracking-tight nx-numeric text-[var(--nx-text-primary)]">
                  {t.token}
                </span>
                <span className="text-xs text-[var(--nx-text-muted)] mt-1 truncate max-w-full">
                  {t.station}
                </span>
              </div>
            ))}
            {preparingTokens.length === 0 && (
              <div className="col-span-3 py-16 text-center text-sm text-[var(--nx-text-muted)]">
                No orders currently in preparation
              </div>
            )}
          </div>
        </section>

        {/* Ready Column */}
        <section aria-labelledby="ready-heading" className="flex flex-col rounded-3xl bg-[var(--nx-surface-card)] border border-[var(--nx-status-success)] p-6 shadow-md ring-1 ring-[var(--nx-status-success)]/20">
          <div className="border-b border-[var(--nx-border-subtle)] pb-3 mb-6 flex justify-between items-center">
            <h2 id="ready-heading" className="text-lg font-bold tracking-wider text-[var(--nx-status-success-text)] uppercase">
              Now Serving ({readyTokens.length})
            </h2>
            <span className="text-xs px-2.5 py-1 rounded-full bg-[var(--nx-status-success-subtle)] text-[var(--nx-status-success-text)] font-semibold animate-pulse">
              Ready for Pickup
            </span>
          </div>

          <div className="flex-1 overflow-y-auto grid grid-cols-2 gap-5 auto-rows-max">
            {readyTokens.map((t) => (
              <div
                key={t.token}
                className="min-h-[96px] rounded-2xl bg-[var(--nx-status-success-subtle)] border-2 border-[var(--nx-status-success)] flex flex-col items-center justify-center p-4 text-center shadow-lg"
              >
                <span className="text-5xl font-black tracking-tight nx-numeric text-[var(--nx-status-success-text)] animate-bounce">
                  {t.token}
                </span>
                <span className="text-xs font-bold text-[var(--nx-status-success-text)] mt-1 tracking-wider uppercase">
                  Collect at Counter
                </span>
              </div>
            ))}
            {readyTokens.length === 0 && (
              <div className="col-span-2 py-16 text-center text-sm text-[var(--nx-text-muted)]">
                Ready orders will appear here
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
};
