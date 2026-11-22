'use client';

import React from 'react';
import { NexusBadge, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph } from '../../../app/components/NexusGlyph';

export interface SplitTenderReceiptPreviewProps {
  readonly completedDigest: string;
  readonly due: number;
  readonly currency: string;
  readonly changeDue: string;
  readonly onDone: () => void;
}

export function SplitTenderReceiptPreview({
  completedDigest,
  due,
  currency,
  changeDue,
  onDone,
}: SplitTenderReceiptPreviewProps): React.JSX.Element {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Payment completed receipt"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 200,
        backgroundColor: 'rgba(3, 6, 12, 0.72)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          borderRadius: '12px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '14px',
        }}
      >
        <div
          style={{
            width: '44px',
            height: '44px',
            borderRadius: '9999px',
            backgroundColor: 'var(--nx-status-success-subtle)',
            color: 'var(--nx-status-success-text)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <NexusGlyph name="check_circle" size={26} />
        </div>
        <NexusText variant="h3">Payment Settled</NexusText>
        <NexusText variant="caption" role="muted">
          Thermal ESC/POS print job spooled silently to 80mm station printer.
        </NexusText>

        <div
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: '8px',
            backgroundColor: 'var(--nx-surface-subtle)',
            border: '1px solid var(--nx-border-subtle)',
          }}
        >
          <NexusStack gap="4px">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <NexusText variant="caption" role="muted">Amount Settled</NexusText>
              <NexusText variant="code" tabular style={{ fontWeight: 700 }}>
                {currency} {due.toFixed(2)}
              </NexusText>
            </div>
            {parseFloat(changeDue) > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--nx-status-success-text)' }}>
                <NexusText variant="caption">Change Returned</NexusText>
                <NexusText variant="code" tabular style={{ fontWeight: 700 }}>
                  {currency} {changeDue}
                </NexusText>
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <NexusText variant="caption" role="muted">SHA-256 Digest</NexusText>
              <NexusText variant="code" style={{ fontSize: '10px' }}>
                {completedDigest.slice(0, 16)}…
              </NexusText>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <NexusText variant="caption" role="muted">Cash Drawer</NexusText>
              <NexusBadge variant="success" dot label="Kicked (RJ11 Pulse)" />
            </div>
          </NexusStack>
        </div>

        <NexusButton variant="primary" onClick={onDone} style={{ width: '100%' }}>
          <NexusText variant="label" style={{ color: 'var(--nx-action-text)', fontWeight: 600 }}>
            Done (Next Order)
          </NexusText>
        </NexusButton>
      </div>
    </div>
  );
}
