'use client';

import React from 'react';
import { NexusButton, NexusCard, NexusStack, NexusText } from '@nexus/ui';

export interface BillingInvoice {
  readonly id: string;
  readonly date: string;
  readonly amount: string;
  readonly card: string;
  readonly hash: string;
}

export interface BillingInvoicesTableProps {
  readonly invoices: readonly BillingInvoice[];
  readonly onDownload: (invoiceId: string) => void;
}

export function BillingInvoicesTable({ invoices, onDownload }: BillingInvoicesTableProps): React.JSX.Element {
  return (
    <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
      <NexusStack gap="var(--nx-space-3)">
        <NexusText variant="h3">Audited Invoices & WORM Statements</NexusText>
        <div style={{ overflowX: 'auto' }}>
          <table className="nx-data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--nx-border-default)', textAlign: 'left' }}>
                <th style={{ padding: '10px 12px' }}>Invoice Number</th>
                <th style={{ padding: '10px 12px' }}>Date</th>
                <th style={{ padding: '10px 12px' }}>Amount</th>
                <th style={{ padding: '10px 12px' }}>Payment Method</th>
                <th style={{ padding: '10px 12px' }}>SHA-256 Digest</th>
                <th style={{ padding: '10px 12px', textAlign: 'right' }}>WORM Proof</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id} style={{ borderBottom: '1px solid var(--nx-border-subtle)' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 700, fontFamily: 'var(--font-mono, monospace)' }}>
                    {inv.id}
                  </td>
                  <td style={{ padding: '10px 12px', color: 'var(--nx-text-secondary)' }}>{inv.date}</td>
                  <td style={{ padding: '10px 12px', fontWeight: 700, color: 'var(--nx-status-success)' }}>
                    {inv.amount}
                  </td>
                  <td style={{ padding: '10px 12px', color: 'var(--nx-text-secondary)' }}>{inv.card}</td>
                  <td style={{ padding: '10px 12px', color: 'var(--nx-text-muted)', fontFamily: 'var(--font-mono, monospace)', fontSize: '11px' }}>
                    {inv.hash}
                  </td>
                  <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                    <NexusButton variant="outline" size="sm" onClick={() => onDownload(inv.id)}>
                      <NexusText variant="caption">Download PDF</NexusText>
                    </NexusButton>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </NexusStack>
    </NexusCard>
  );
}
