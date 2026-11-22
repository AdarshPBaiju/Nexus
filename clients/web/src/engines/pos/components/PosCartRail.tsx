'use client';

import React from 'react';
import { NexusBadge, NexusText } from '@nexus/ui';
import type { PosCartItem, PosCartSummary, PosHeldTab } from '../types';
import { PosCartLineItem } from './PosCartLineItem';
import { PosCartTotalsFooter } from './PosCartTotalsFooter';
import { NexusGlyph } from '../../../app/components/NexusGlyph';

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
  const isEmpty = items.length === 0;

  return (
    <section className="nx-pos-panel" aria-label="Current order">
      <div
        style={{
          flexShrink: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '8px',
          padding: '10px 12px',
          borderBottom: '1px solid var(--nx-border-subtle)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
          <NexusText variant="h4">Current order</NexusText>
          <NexusBadge variant="neutral" label={`${summary.itemCount} items`} />
        </div>
        <button
          type="button"
          onClick={onClear}
          disabled={isEmpty}
          className="nx-focusable"
          style={{
            border: 'none',
            background: 'transparent',
            cursor: isEmpty ? 'not-allowed' : 'pointer',
            opacity: isEmpty ? 0.5 : 1,
            color: 'var(--nx-status-danger-text)',
            fontSize: '11px',
            fontWeight: 600,
            padding: '2px 4px',
          }}
        >
          Clear
        </button>
      </div>

      <div className="nx-scroll-area" style={{ flex: 1, minHeight: 0, padding: '8px 10px' }}>
        {isEmpty ? (
          <div
            style={{
              height: '100%',
              minHeight: '160px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              textAlign: 'center',
            }}
          >
            <NexusGlyph name="shopping_bag" size={30} color="var(--nx-text-muted)" />
            <NexusText variant="label">No items in this order</NexusText>
            <NexusText variant="caption" role="muted">
              Select a product or scan a SKU barcode.
            </NexusText>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {items.map((item) => (
              <PosCartLineItem
                key={item.id}
                item={item}
                onUpdateQuantity={onUpdateQuantity}
                onRequestVoid={onRequestVoid}
              />
            ))}
          </div>
        )}
      </div>

      <PosCartTotalsFooter
        summary={summary}
        heldTabs={heldTabs}
        isEmpty={isEmpty}
        onApplyDiscount={onApplyDiscount}
        onHoldTab={onHoldTab}
        onOpenPay={onOpenPay}
      />
    </section>
  );
};
