'use client';

import React from 'react';
import { NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { PosCartSummary, PosHeldTab } from '../types';

export interface PosCartTotalsFooterProps {
  readonly summary: PosCartSummary;
  readonly heldTabs: readonly PosHeldTab[];
  readonly isEmpty: boolean;
  readonly onApplyDiscount: (percent: number) => void;
  readonly onHoldTab: () => void;
  readonly onOpenPay: () => void;
}

export function PosCartTotalsFooter({
  summary,
  heldTabs,
  isEmpty,
  onApplyDiscount,
  onHoldTab,
  onOpenPay,
}: PosCartTotalsFooterProps): React.JSX.Element {
  return (
    <div
      style={{
        flexShrink: 0,
        padding: '10px 12px 12px',
        borderTop: '1px solid var(--nx-border-subtle)',
        backgroundColor: 'var(--nx-surface-subtle)',
      }}
    >
      <div style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
        {[
          { label: 'Staff 15%', val: 15 },
          { label: 'VIP 20%', val: 20 },
          { label: 'Comp 100%', val: 100 },
        ].map((d) => (
          <NexusButton
            key={d.val}
            variant="outline"
            size="sm"
            disabled={isEmpty}
            onClick={() => onApplyDiscount(d.val)}
          >
            <NexusText variant="caption">{d.label}</NexusText>
          </NexusButton>
        ))}
      </div>

      <NexusStack gap="3px" style={{ marginBottom: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <NexusText variant="caption" role="muted">Subtotal</NexusText>
          <NexusText variant="code" tabular>${summary.subtotal}</NexusText>
        </div>
        {parseFloat(summary.discount) > 0 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--nx-status-success-text)' }}>
            <NexusText variant="caption">Discount</NexusText>
            <NexusText variant="code" tabular>-${summary.discount}</NexusText>
          </div>
        )}
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <NexusText variant="caption" role="muted">Sales Tax</NexusText>
          <NexusText variant="code" tabular>${summary.tax}</NexusText>
        </div>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'baseline',
            paddingTop: '6px',
            borderTop: '1px solid var(--nx-border-subtle)',
          }}
        >
          <NexusText variant="h3">Total Due</NexusText>
          <NexusText
            variant="h2"
            tabular
            style={{ color: 'var(--nx-action-primary)', fontWeight: 800 }}
          >
            ${summary.total}
          </NexusText>
        </div>
      </NexusStack>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '6px' }}>
        <NexusButton
          variant="outline"
          disabled={isEmpty}
          onClick={onHoldTab}
          title="Park current order without voiding"
        >
          <NexusText variant="caption">Hold ({heldTabs.length})</NexusText>
        </NexusButton>

        <NexusButton
          variant="primary"
          disabled={isEmpty}
          onClick={onOpenPay}
          title="Open split tender dialog (F4)"
        >
          <NexusText variant="label" style={{ fontWeight: 700, color: 'var(--nx-action-text)' }}>
            CHARGE · ${summary.total}
          </NexusText>
        </NexusButton>
      </div>
    </div>
  );
}
