'use client';

import React, { useEffect, useState } from 'react';
import type { KdsStationType, KdsTicketDto } from './kds.types';

export interface KdsTouchCanvasProps {
  readonly tickets: readonly KdsTicketDto[];
  readonly onBumpTicket: (ticketId: string) => void;
  readonly onRecallTicket: () => void;
  readonly activeStation: KdsStationType;
  readonly onStationChange: (station: KdsStationType) => void;
}

export const KdsTouchCanvas: React.FC<KdsTouchCanvasProps> = ({
  tickets,
  onBumpTicket,
  onRecallTicket,
  activeStation,
  onStationChange,
}) => {
  const filtered = tickets.filter((t) => t.stationType === activeStation && t.status !== 'SERVED');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.key === ' ' || e.key === 'Enter') && filtered.length > 0) {
        e.preventDefault();
        onBumpTicket(filtered[0].id);
      } else if (e.ctrlKey && e.key === 'z') {
        e.preventDefault();
        onRecallTicket();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filtered, onBumpTicket, onRecallTicket]);

  const getSlaClass = (elapsed: number, sla: number) => {
    if (elapsed < sla * 0.6) return 'bg-[var(--nx-status-success-subtle)] text-[var(--nx-status-success-text)]';
    if (elapsed <= sla) return 'bg-[var(--nx-status-warning-subtle)] text-[var(--nx-status-warning-text)]';
    return 'bg-[var(--nx-status-danger-subtle)] text-[var(--nx-status-danger-text)] animate-pulse';
  };

  return (
    <div className="w-full h-full min-h-screen bg-[var(--nx-surface-bg)] text-[var(--nx-text-primary)] flex flex-col font-sans select-none">
      {/* 44px Top Status Bar */}
      <header className="h-[44px] px-6 bg-[var(--nx-surface-card)] border-b border-[var(--nx-border-default)] flex justify-between items-center text-sm font-medium">
        <div className="flex gap-2">
          {(['BARISTA', 'HOT_KITCHEN', 'BAKERY', 'EXPO'] as const).map((st) => (
            <button
              key={st}
              type="button"
              onClick={() => onStationChange(st)}
              className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                activeStation === st
                  ? 'bg-[var(--nx-action-primary)] text-[var(--nx-action-text)]'
                  : 'bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold">
          <span className="text-[var(--nx-text-secondary)]">Queue: {filtered.length} active</span>
          <button
            type="button"
            onClick={onRecallTicket}
            className="px-2.5 py-1 rounded bg-[var(--nx-surface-subtle)] border border-[var(--nx-border-subtle)] text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]"
          >
            Recall (Ctrl+Z)
          </button>
        </div>
      </header>

      {/* Ticket Grid */}
      <main className="flex-1 p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 auto-rows-max overflow-y-auto">
        {filtered.map((ticket) => (
          <article
            key={ticket.id}
            className="rounded-2xl bg-[var(--nx-surface-card)] border border-[var(--nx-border-default)] flex flex-col shadow-sm overflow-hidden"
          >
            <div className="p-4 border-b border-[var(--nx-border-subtle)] flex justify-between items-center bg-[var(--nx-surface-subtle)]">
              <div>
                <span className="text-2xl font-black nx-numeric tracking-tight text-[var(--nx-text-primary)]">
                  {ticket.orderToken}
                </span>
                <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded bg-[var(--nx-surface-card)] border border-[var(--nx-border-subtle)] text-[var(--nx-text-muted)]">
                  {ticket.diningType || 'Dine In'}
                </span>
              </div>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold nx-numeric ${getSlaClass(ticket.elapsedSeconds, ticket.slaSeconds)}`}>
                {Math.floor(ticket.elapsedSeconds / 60)}:{(ticket.elapsedSeconds % 60).toString().padStart(2, '0')}
              </span>
            </div>

            <div className="flex-1 p-4 space-y-3">
              {ticket.lines.map((line) => (
                <div key={line.id} className="text-sm">
                  <div className="flex justify-between font-semibold text-[var(--nx-text-primary)]">
                    <span>{line.itemName}</span>
                    <span className="nx-numeric">x{line.quantity}</span>
                  </div>
                  {line.allergenFlags.length > 0 && (
                    <div className="mt-1 px-2 py-0.5 rounded bg-[var(--nx-status-danger-subtle)] text-[var(--nx-status-danger-text)] text-xs font-bold inline-block">
                      ⚠️ ALLERGEN: {line.allergenFlags.join(', ')}
                    </div>
                  )}
                  {line.modifierNotes.length > 0 && (
                    <div className="text-xs text-[var(--nx-text-secondary)] mt-0.5 space-x-1">
                      {line.modifierNotes.map((note) => (
                        <span key={note} className="inline-block px-1.5 py-0.5 rounded bg-[var(--nx-surface-selected)] font-medium">
                          {note}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="p-3 bg-[var(--nx-surface-subtle)] border-t border-[var(--nx-border-subtle)]">
              <button
                type="button"
                onClick={() => onBumpTicket(ticket.id)}
                className="w-full min-h-[44px] rounded-xl bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-bold text-sm tracking-wide uppercase hover:bg-[var(--nx-action-primary-hover)] transition-all flex items-center justify-center gap-2"
              >
                <span>Bump Ticket</span>
                <span className="text-xs font-normal opacity-80">(Space)</span>
              </button>
            </div>
          </article>
        ))}
      </main>
    </div>
  );
};
