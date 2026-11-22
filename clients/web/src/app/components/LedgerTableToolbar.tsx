'use client';

import React from 'react';
import Link from 'next/link';
import { NexusButton, NexusSelect, NexusText } from '@nexus/ui';

export type TableDensity = 'compact' | 'comfortable' | 'touch';
export type CurrencyCode = 'USD' | 'INR' | 'EUR' | 'GBP' | 'AED';

export interface LedgerTableToolbarProps {
  readonly currency: CurrencyCode;
  readonly onCurrencyChange: (c: CurrencyCode) => void;
  readonly density: TableDensity;
  readonly onDensityChange: (d: TableDensity) => void;
}

export function LedgerTableToolbar({
  currency,
  onCurrencyChange,
  density,
  onDensityChange,
}: LedgerTableToolbarProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
            Audited Sales & Ledger Stream
          </NexusText>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: 'var(--nx-surface-subtle)',
              padding: '3px 8px',
              borderRadius: '6px',
              border: '1px solid var(--nx-border-subtle)',
            }}
          >
            <span
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: 'var(--nx-status-success)',
                display: 'inline-block',
              }}
            />
            <NexusText variant="code" style={{ fontSize: '11px', color: 'var(--nx-text-primary)' }}>
              Live WS Stream · 34 msg/s
            </NexusText>
          </div>
        </div>
        <NexusText variant="caption" role="muted" style={{ marginTop: '2px' }}>
          Keyset 2D virtualized audit ledger with sub-millisecond query proofs.
        </NexusText>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        {/* Dynamic Currency Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <NexusText variant="caption" role="muted">CURRENCY:</NexusText>
          <div style={{ width: '130px' }}>
            <NexusSelect
              value={currency}
              onChange={(val: string) => onCurrencyChange(val as CurrencyCode)}
              options={[
                { value: 'USD', label: '$ USD' },
                { value: 'INR', label: '₹ INR' },
                { value: 'EUR', label: '€ EUR' },
                { value: 'GBP', label: '£ GBP' },
                { value: 'AED', label: 'د.إ AED' },
              ]}
            />
          </div>
        </div>

        {/* Density Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <NexusText variant="caption" role="muted">DENSITY:</NexusText>
          {(['compact', 'comfortable', 'touch'] as const).map((d) => (
            <NexusButton
              key={d}
              variant={density === d ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => onDensityChange(d)}
            >
              {d[0].toUpperCase()}
            </NexusButton>
          ))}
        </div>

        <Link href="/pos">
          <NexusButton variant="primary" size="sm">
            Open Counter POS &rarr;
          </NexusButton>
        </Link>
      </div>
    </div>
  );
}
