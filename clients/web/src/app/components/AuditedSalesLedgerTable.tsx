'use client';

import React, { useState } from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { AuditedRowExpandedDrawer } from './AuditedRowExpandedDrawer';
import {
  LedgerTableToolbar,
  type CurrencyCode,
  type TableDensity,
} from './LedgerTableToolbar';

const CURRENCY_SYMBOLS: Record<CurrencyCode, string> = {
  USD: '$',
  INR: '₹',
  EUR: '€',
  GBP: '£',
  AED: 'د.إ ',
};

interface TransactionRow {
  readonly id: string;
  readonly time: string;
  readonly cashier: string;
  readonly tender: string;
  readonly amountNum: number;
  readonly status: string;
}

const INITIAL_TRANSACTIONS: readonly TransactionRow[] = [
  { id: 'TXN-9021', time: '12:04:18', cashier: 'Sarah J.', tender: 'CASH', amountNum: 12.50, status: 'SETTLED' },
  { id: 'TXN-9022', time: '12:05:42', cashier: 'Marcus V.', tender: 'STRIPE_EDC', amountNum: 24.80, status: 'SETTLED' },
  { id: 'TXN-9023', time: '12:06:11', cashier: 'Chloe B.', tender: 'UPI_QR', amountNum: 8.20, status: 'SETTLED' },
  { id: 'TXN-9024', time: '12:07:05', cashier: 'Sarah J.', tender: 'SPLIT_TENDER', amountNum: 45.00, status: 'SETTLED' },
  { id: 'TXN-9025', time: '12:08:33', cashier: 'David C.', tender: 'RAZORPAY_EDC', amountNum: 18.90, status: 'SETTLED' },
];

export function AuditedSalesLedgerTable(): React.JSX.Element {
  const [density, setDensity] = useState<TableDensity>('comfortable');
  const [currency, setCurrency] = useState<CurrencyCode>('USD');
  const [expandedRowId, setExpandedRowId] = useState<string | null>(null);

  const currencySymbol = CURRENCY_SYMBOLS[currency];

  const paddingStyle = {
    compact: '6px 12px',
    comfortable: '10px 14px',
    touch: '14px 16px',
  }[density];

  const toggleExpand = (id: string) => {
    setExpandedRowId((prev) => (prev === id ? null : id));
  };

  return (
    <NexusBox
      className="nx-panel"
      style={{
        borderRadius: '12px',
        border: '1px solid var(--nx-border-default)',
        padding: '20px',
      }}
    >
      <NexusStack gap="16px">
        <LedgerTableToolbar
          currency={currency}
          onCurrencyChange={setCurrency}
          density={density}
          onDensityChange={setDensity}
        />

        {/* Keyset 0-OFFSET Telemetry Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '6px 12px',
            backgroundColor: 'var(--nx-surface-subtle)',
            borderRadius: '6px',
            border: '1px solid var(--nx-border-subtle)',
            fontSize: '11px',
            fontFamily: 'monospace',
            flexWrap: 'wrap',
            gap: '8px',
          }}
        >
          <div>
            Showing <strong style={{ color: 'var(--nx-text-primary)' }}>1–5</strong> of 2,481 entries (Filtered from 124.9k)
          </div>
          <div style={{ display: 'flex', gap: '12px', color: 'var(--nx-text-muted)' }}>
            <span>WINDOW: <strong style={{ color: 'var(--nx-status-success)' }}>0.8ms (0 SQL OFFSET)</strong></span>
            <span>•</span>
            <span>KEYSET: <strong style={{ color: 'var(--nx-text-primary)' }}>0x7FA949C128</strong></span>
            <span>•</span>
            <span>BUFFER: <strong style={{ color: 'var(--nx-action-primary)' }}>14.2 MB / 60 FPS</strong></span>
          </div>
        </div>

        {/* Table Data */}
        <div style={{ overflowX: 'auto' }}>
          <table className="nx-data-table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--nx-border-default)', color: 'var(--nx-text-muted)', fontSize: '11px' }}>
                <th style={{ padding: '8px 12px' }}>TXN ID</th>
                <th style={{ padding: '8px 12px' }}>TIMESTAMP</th>
                <th style={{ padding: '8px 12px' }}>CASHIER</th>
                <th style={{ padding: '8px 12px' }}>TENDER RAIL</th>
                <th style={{ padding: '8px 12px' }}>SETTLED AMOUNT</th>
                <th style={{ padding: '8px 12px' }}>INTEGRITY</th>
                <th style={{ padding: '8px 12px', textAlign: 'right' }}>FORENSIC DETAILS</th>
              </tr>
            </thead>
            <tbody>
              {INITIAL_TRANSACTIONS.map((tx) => {
                const isExpanded = expandedRowId === tx.id;
                return (
                  <React.Fragment key={tx.id}>
                    <tr
                      style={{
                        borderBottom: isExpanded ? 'none' : '1px solid var(--nx-border-subtle)',
                        backgroundColor: isExpanded ? 'var(--nx-surface-selected)' : 'transparent',
                        transition: 'background-color 0.1s ease',
                      }}
                    >
                      <td style={{ padding: paddingStyle, fontFamily: 'monospace', fontWeight: 700 }}>
                        {tx.id}
                      </td>
                      <td style={{ padding: paddingStyle, fontFamily: 'monospace', color: 'var(--nx-text-secondary)' }}>
                        {tx.time}
                      </td>
                      <td style={{ padding: paddingStyle }}>{tx.cashier}</td>
                      <td style={{ padding: paddingStyle }}>
                        <NexusBadge variant="neutral" label={tx.tender} />
                      </td>
                      <td style={{ padding: paddingStyle }}>
                        {/* Dynamic Currency Icon Badge */}
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                          <span
                            style={{
                              padding: '2px 6px',
                              borderRadius: '4px',
                              backgroundColor: 'var(--nx-surface-subtle)',
                              border: '1px solid var(--nx-border-default)',
                              fontSize: '11px',
                              fontWeight: 700,
                              color: 'var(--nx-action-primary)',
                              fontFamily: 'monospace',
                            }}
                          >
                            {currencySymbol.trim()}
                          </span>
                          <span style={{ fontFamily: 'monospace', fontWeight: 700 }} className="nx-numeric">
                            {tx.amountNum.toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td style={{ padding: paddingStyle }}>
                        <NexusBadge variant="success" label="SHA256:VERIFIED" />
                      </td>
                      <td style={{ padding: paddingStyle, textAlign: 'right' }}>
                        <NexusButton
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpand(tx.id)}
                        >
                          {isExpanded ? 'Collapse ▲' : 'Inspect ▼'}
                        </NexusButton>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr>
                        <td colSpan={7} style={{ padding: 0 }}>
                          <AuditedRowExpandedDrawer
                            txnId={tx.id}
                            tender={tx.tender}
                            currencySymbol={currencySymbol}
                            amount={tx.amountNum.toFixed(2)}
                          />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
