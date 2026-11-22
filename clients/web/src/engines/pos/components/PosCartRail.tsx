'use client';

import React from 'react';
import { NexusButton } from '@nexus/ui';
import type { PosCartItem, PosCartSummary, PosHeldTab } from '../types';

export interface PosCartRailProps {
  readonly items: readonly PosCartItem[];
  readonly summary: PosCartSummary;
  readonly heldTabs: readonly PosHeldTab[];
  readonly onClear: () => void;
  readonly onUpdateQuantity: (id: string, delta: number) => void;
  readonly onRequestVoid: (id: string) => void;
  readonly onApplyDiscount: (percent: number) => void;
  readonly onHoldTab: () => void;
  readonly onOpenPay: () => void;
}

export const PosCartRail: React.FC<PosCartRailProps> = ({
  items,
  summary,
  heldTabs,
  onClear,
  onUpdateQuantity,
  onRequestVoid,
  onApplyDiscount,
  onHoldTab,
  onOpenPay,
}) => {
  return (
    <div className="col-span-4 flex flex-col rounded-2xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-3 overflow-hidden">
      <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-2">
        <h3 className="text-xs font-bold text-[var(--nx-text-primary)]">Folio Cart ({summary.itemCount})</h3>
        <button onClick={onClear} type="button" className="text-[11px] text-outline hover:text-error">Clear All</button>
      </div>

      {/* Cart Items */}
      <div className="my-2 flex-1 overflow-y-auto space-y-1.5 pr-1">
        {items.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-outline text-xs text-center space-y-1">
            <span className="material-symbols-outlined text-[32px]">shopping_cart</span>
            <span>Cart is empty</span>
            <span className="text-[10px]">Select items from menu or scan SKU</span>
          </div>
        ) : (
          items.map((it) => (
            <div key={it.id} className="rounded-xl bg-[var(--nx-surface-subtle)] p-2 text-xs flex justify-between items-center">
              <div className="flex-1 pr-2">
                <div className="font-semibold text-[var(--nx-text-primary)]">{it.name}</div>
                {it.selectedModifiers && it.selectedModifiers.length > 0 && (
                  <div className="text-[10px] text-outline font-mono">
                    {it.selectedModifiers.map((m) => m.optionName).join(', ')}
                  </div>
                )}
                <div className="font-mono text-[11px] text-outline">$ {it.unitPrice} ea</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center bg-surface-container rounded-lg border border-outline-variant">
                  <button onClick={() => onUpdateQuantity(it.id, -1)} className="w-5 h-6 text-center text-xs font-bold text-outline hover:text-on-surface">-</button>
                  <span className="px-1.5 font-mono text-xs font-bold text-on-surface">{it.quantity}</span>
                  <button onClick={() => onUpdateQuantity(it.id, 1)} className="w-5 h-6 text-center text-xs font-bold text-outline hover:text-on-surface">+</button>
                </div>
                <span className="font-mono font-bold text-on-surface w-12 text-right">
                  ${(parseFloat(it.unitPrice) * it.quantity).toFixed(2)}
                </span>
                <button onClick={() => onRequestVoid(it.id)} type="button" className="text-outline hover:text-error text-xs">✕</button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Discounts & Fiscal Totals */}
      <div className="border-t border-[var(--nx-border-subtle)] pt-2 space-y-1 font-mono text-[11px]">
        <div className="flex justify-between items-center pb-1">
          <span className="text-outline">Quick Discount:</span>
          <div className="flex gap-1 text-[10px]">
            {[0, 5, 10, 15].map((d) => (
              <button key={d} type="button" onClick={() => onApplyDiscount(d)} className="px-1.5 py-0.5 rounded bg-surface-container hover:bg-surface-bright text-outline font-bold">
                {d === 0 ? 'None' : `${d}%`}
              </button>
            ))}
          </div>
        </div>
        <div className="flex justify-between text-outline">
          <span>Subtotal:</span>
          <span>$ {summary.subtotal}</span>
        </div>
        {parseFloat(summary.discount) > 0 && (
          <div className="flex justify-between text-secondary">
            <span>Discount:</span>
            <span>-$ {summary.discount}</span>
          </div>
        )}
        <div className="flex justify-between text-outline">
          <span>VAT (10%):</span>
          <span>$ {summary.tax}</span>
        </div>
        <div className="flex justify-between text-sm font-bold text-on-surface pt-1 border-t border-surface-container-highest">
          <span>TOTAL DUE:</span>
          <span className="text-primary font-bold text-base">$ {summary.total}</span>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-2.5 flex gap-2">
        <NexusButton variant="secondary" onClick={onHoldTab} disabled={items.length === 0} className="flex-1 justify-center text-xs">
          Hold (F3){heldTabs.length > 0 ? ` [${heldTabs.length}]` : ''}
        </NexusButton>
        <NexusButton variant="primary" onClick={onOpenPay} disabled={items.length === 0} className="flex-1 justify-center text-xs font-bold">
          Pay (F4) &rarr;
        </NexusButton>
      </div>
    </div>
  );
};
