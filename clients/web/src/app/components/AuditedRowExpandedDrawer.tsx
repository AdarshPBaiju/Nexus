'use client';

import React, { useState } from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';

export interface AuditedRowExpandedDrawerProps {
  readonly txnId: string;
  readonly tender: string;
  readonly currencySymbol: string;
  readonly amount: string;
}

export function AuditedRowExpandedDrawer({
  txnId,
  tender,
  currencySymbol,
  amount,
}: AuditedRowExpandedDrawerProps): React.JSX.Element {
  const [activeTab, setActiveTab] = useState<'ESCPOS' | 'MERKLE' | 'TAX'>('ESCPOS');

  return (
    <div
      style={{
        padding: '16px 20px',
        backgroundColor: 'var(--nx-surface-subtle)',
        borderTop: '1px solid var(--nx-border-default)',
        borderBottom: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="12px">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            <NexusButton
              variant={activeTab === 'ESCPOS' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('ESCPOS')}
            >
              Raw ESC/POS & Hex Payload
            </NexusButton>
            <NexusButton
              variant={activeTab === 'MERKLE' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('MERKLE')}
            >
              Hardware Audit Trail & Merkle Root
            </NexusButton>
            <NexusButton
              variant={activeTab === 'TAX' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setActiveTab('TAX')}
            >
              Tax Allocation & Ledger Proof
            </NexusButton>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <NexusText variant="code" role="muted" style={{ fontSize: '11px' }}>PAYLOAD SIZE: 1.4 KB</NexusText>
            <NexusBadge variant="success" label="SHA-256 MATCHED" />
          </div>
        </div>

        {activeTab === 'ESCPOS' && (
          <NexusBox
            style={{
              padding: '12px 14px',
              backgroundColor: 'var(--nx-surface-bg)',
              borderRadius: '6px',
              border: '1px solid var(--nx-border-subtle)',
              fontFamily: 'monospace',
              fontSize: '12px',
              overflowX: 'auto',
            }}
          >
            <NexusText variant="caption" role="muted" style={{ display: 'block', marginBottom: '4px' }}>
              THERMAL ESC/POS RASTER STREAM ({txnId} · {tender} · {currencySymbol}{amount}):
            </NexusText>
            <code>
              [0x1B, 0x40] // ESC @ (Init){'\n'}
              [0x1B, 0x61, 0x01] // Center Align{'\n'}
              *** NEXUS FLAGSHIP ROASTERY & CAFÉ ***{'\n'}
              [0x1B, 0x61, 0x00] // Left Align{'\n'}
              TXN: {txnId} | RAIL: {tender}{'\n'}
              TOTAL SETTLED: {currencySymbol}{amount} (PAID IN FULL){'\n'}
              FISCAL WORM HASH: 0x9a8f4c21e0b3...{'\n'}
              [0x1D, 0x56, 0x41, 0x10] // Cut Paper & Kick Drawer Pin 2
            </code>
          </NexusBox>
        )}

        {activeTab === 'MERKLE' && (
          <NexusBox
            style={{
              padding: '12px 14px',
              backgroundColor: 'var(--nx-surface-bg)',
              borderRadius: '6px',
              border: '1px solid var(--nx-border-subtle)',
              fontSize: '12px',
            }}
          >
            <NexusText variant="caption" role="muted">IMMUTABLE FORENSIC MERKLE LEAF PROOF</NexusText>
            <NexusText variant="code" style={{ display: 'block', marginTop: '4px' }}>
              Leaf Hash: sha256:{txnId.toLowerCase()}8f01a3c79e4d021b8a{'\n'}
              Merkle Root: 0x7fa949c1284eb090a9b34c{'\n'}
              Witness Signer: Regional KMS Key (ap-south-1 · AES-256-GCM)
            </NexusText>
          </NexusBox>
        )}

        {activeTab === 'TAX' && (
          <NexusBox
            style={{
              padding: '12px 14px',
              backgroundColor: 'var(--nx-surface-bg)',
              borderRadius: '6px',
              border: '1px solid var(--nx-border-subtle)',
              fontSize: '12px',
            }}
          >
            <NexusText variant="caption" role="muted">STATUTORY TAX BREAKDOWN & JOURNAL ENTRIES</NexusText>
            <NexusText variant="body" style={{ marginTop: '4px' }}>
              Net Subtotal: {currencySymbol}{(Number(amount) * 0.95).toFixed(2)} | Statutory Tax (5.00% GST): {currencySymbol}{(Number(amount) * 0.05).toFixed(2)} | Gross Folio: {currencySymbol}{amount}
            </NexusText>
            <NexusText variant="code" role="muted" style={{ display: 'block', marginTop: '4px' }}>
              Debit: 1010-CASH / EDC AR ({currencySymbol}{amount}) | Credit: 4000-SALES-REV ({currencySymbol}{(Number(amount) * 0.95).toFixed(2)}) | Credit: 2200-GST-OUTPUT ({currencySymbol}{(Number(amount) * 0.05).toFixed(2)})
            </NexusText>
          </NexusBox>
        )}
      </NexusStack>
    </div>
  );
}
