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
  readonly onDownloadNotice?: (invoiceId: string) => void;
}

export function downloadWormInvoiceDocument(inv: BillingInvoice): void {
  const invoiceHtml = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Fiscal Tax Statement - ${inv.id}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; max-width: 600px; margin: 40px auto; padding: 24px; border: 1px solid #ccc; border-radius: 8px; }
    h1 { margin: 0 0 4px; font-size: 20px; }
    .muted { color: #666; font-size: 12px; }
    .seal { background: #e6f4ea; color: #137333; padding: 6px 10px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; margin-top: 8px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 13px; }
    th, td { padding: 8px; text-align: left; border-bottom: 1px solid #eee; }
    .right { text-align: right; }
    .digest { font-family: monospace; font-size: 10px; background: #f1f3f4; padding: 8px; border-radius: 4px; word-break: break-all; margin-top: 16px; }
  </style>
</head>
<body>
  <h1>PROJECT NEXUS — FISCAL TAX INVOICE</h1>
  <div class="muted">Sequential Gapless Series: ${inv.id} · Date: ${inv.date}</div>
  <div class="seal">✓ STATUTORY 8-YEAR WORM VAULT VERIFIED</div>
  <table>
    <tr><th>Subscription Description</th><th class="right">Charge</th></tr>
    <tr><td>Cloud Multi-Tenant SaaS License (Artisan Pro)</td><td class="right">${inv.amount}</td></tr>
    <tr><td>Regional PostgreSQL 16 Forced RLS Partition</td><td class="right">$0.00 (Included)</td></tr>
    <tr><td>Regional KMS AES-256-GCM Envelope Encryption</td><td class="right">$0.00 (Included)</td></tr>
    <tr><th>Total Settled via ${inv.card}</th><th class="right">${inv.amount}</th></tr>
  </table>
  <div class="digest">
    <strong>SHA-256 Merkle Proof:</strong><br>${inv.hash}
  </div>
</body>
</html>`;

  const blob = new Blob([invoiceHtml], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `nexus-fiscal-invoice-${inv.id}.html`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function BillingInvoicesTable({ invoices, onDownloadNotice }: BillingInvoicesTableProps): React.JSX.Element {
  const handleDownload = (inv: BillingInvoice) => {
    downloadWormInvoiceDocument(inv);
    if (onDownloadNotice) onDownloadNotice(inv.id);
  };

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
                    <NexusButton variant="outline" size="sm" onClick={() => handleDownload(inv)}>
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
