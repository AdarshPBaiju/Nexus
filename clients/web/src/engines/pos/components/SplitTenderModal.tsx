'use client';

import React, { useMemo, useState } from 'react';
import { NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { SplitTenderEntry } from '../types';
import { SplitTenderReceiptPreview } from './SplitTenderReceiptPreview';
import { SplitTenderRailInput } from './SplitTenderRailInput';

export interface SplitTenderModalProps {
  readonly isOpen: boolean;
  readonly totalDue: string;
  readonly currency: string;
  readonly onClose: () => void;
  readonly onCompletePayment: (tenders: readonly SplitTenderEntry[]) => Promise<void>;
}

const QUICK_CASH = [5, 10, 20, 50, 100];

export const SplitTenderModal: React.FC<SplitTenderModalProps> = ({
  isOpen,
  totalDue,
  currency,
  onClose,
  onCompletePayment,
}) => {
  const due = parseFloat(totalDue) || 0;
  const [cashTendered, setCashTendered] = useState('');
  const [cardAmount, setCardAmount] = useState('');
  const [qrAmount, setQrAmount] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [completedDigest, setCompletedDigest] = useState<string | null>(null);

  const cashApplied = parseFloat(cashTendered) || 0;
  const cardApplied = parseFloat(cardAmount) || 0;
  const qrApplied = parseFloat(qrAmount) || 0;

  const totalApplied = useMemo(
    () => cardApplied + qrApplied + Math.min(cashApplied, Math.max(0, due - cardApplied - qrApplied)),
    [cardApplied, qrApplied, cashApplied, due]
  );

  const changeDue = useMemo(() => {
    const cashPortion = Math.max(0, due - cardApplied - qrApplied);
    return Math.max(0, cashApplied - cashPortion).toFixed(2);
  }, [cardApplied, qrApplied, cashApplied, due]);

  const remaining = Math.max(0, due - totalApplied).toFixed(2);
  const isSettled = totalApplied >= due && due > 0;

  if (!isOpen) return null;

  const reset = () => {
    setCompletedDigest(null);
    setCashTendered('');
    setCardAmount('');
    setQrAmount('');
    setIsProcessing(false);
    onClose();
  };

  const handleSubmit = async () => {
    if (!isSettled || isProcessing) return;
    setIsProcessing(true);

    const tenders: SplitTenderEntry[] = [];
    if (cashApplied > 0) {
      const applied = Math.min(cashApplied, Math.max(0, due - cardApplied - qrApplied));
      tenders.push({
        tenderType: 'CASH',
        amount: applied.toFixed(2),
        tenderedAmount: cashApplied.toFixed(2),
        changeReturned: changeDue,
      });
    }
    if (cardApplied > 0) {
      tenders.push({
        tenderType: 'CARD',
        amount: cardApplied.toFixed(2),
        tenderedAmount: cardApplied.toFixed(2),
        changeReturned: '0.00',
      });
    }
    if (qrApplied > 0) {
      tenders.push({
        tenderType: 'DIGITAL_QR',
        amount: qrApplied.toFixed(2),
        tenderedAmount: qrApplied.toFixed(2),
        changeReturned: '0.00',
      });
    }

    try {
      await onCompletePayment(tenders);
      const digest = Array.from(crypto.getRandomValues(new Uint8Array(16)))
        .map((b) => b.toString(16).padStart(2, '0'))
        .join('');
      setCompletedDigest(digest);
    } catch {
      setIsProcessing(false);
    }
  };

  if (completedDigest) {
    return (
      <SplitTenderReceiptPreview
        completedDigest={completedDigest}
        due={due}
        currency={currency}
        changeDue={changeDue}
        onDone={reset}
      />
    );
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Split tender checkout"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 200,
        backgroundColor: 'rgba(3, 6, 12, 0.65)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '480px',
          borderRadius: '12px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <NexusText variant="h3">Multi-Rail Tender</NexusText>
            <NexusText variant="caption" role="muted">Combine Cash, Card EDC, and UPI QR</NexusText>
          </div>
          <button
            type="button"
            onClick={reset}
            className="nx-focusable"
            style={{
              border: 'none',
              background: 'transparent',
              fontSize: '18px',
              cursor: 'pointer',
              color: 'var(--nx-text-muted)',
            }}
          >
            ✕
          </button>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            borderRadius: '8px',
            backgroundColor: 'var(--nx-surface-subtle)',
            border: '1px solid var(--nx-border-subtle)',
          }}
        >
          <NexusStack gap="0px">
            <NexusText variant="caption" role="muted">Total Due</NexusText>
            <NexusText variant="h2" tabular style={{ color: 'var(--nx-action-primary)', fontWeight: 800 }}>
              {currency} {due.toFixed(2)}
            </NexusText>
          </NexusStack>
          <NexusStack gap="0px" style={{ textAlign: 'end' }}>
            <NexusText variant="caption" role="muted">Remaining to Settle</NexusText>
            <NexusText
              variant="h3"
              tabular
              style={{
                color: parseFloat(remaining) === 0 ? 'var(--nx-status-success-text)' : 'var(--nx-status-warning-text)',
                fontWeight: 700,
              }}
            >
              {currency} {remaining}
            </NexusText>
          </NexusStack>
        </div>

        <NexusStack gap="8px">
          <SplitTenderRailInput
            label="Cash Tender"
            hint="Physical drawer notes & coins"
            value={cashTendered}
            onChange={setCashTendered}
            onFull={() => setCashTendered(due.toFixed(2))}
          />
          <div style={{ display: 'flex', gap: '4px' }}>
            {QUICK_CASH.map((amt) => (
              <NexusButton
                key={amt}
                variant="outline"
                size="sm"
                onClick={() => setCashTendered(String(amt))}
              >
                <NexusText variant="caption">${amt}</NexusText>
              </NexusButton>
            ))}
          </div>
          <SplitTenderRailInput
            label="Card (Stripe / EDC Terminal)"
            hint="Smart POS chip & pin / tap"
            value={cardAmount}
            onChange={setCardAmount}
            onFull={() => setCardAmount(Math.max(0, due - qrApplied).toFixed(2))}
          />
          <SplitTenderRailInput
            label="UPI / Instant Digital QR"
            hint="Dynamic customer pole QR"
            value={qrAmount}
            onChange={setQrAmount}
            onFull={() => setQrAmount(Math.max(0, due - cardApplied).toFixed(2))}
          />
        </NexusStack>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '8px', paddingTop: '6px' }}>
          <NexusButton variant="outline" onClick={reset}>
            <NexusText variant="label">Cancel</NexusText>
          </NexusButton>
          <NexusButton
            variant="primary"
            disabled={!isSettled || isProcessing}
            onClick={handleSubmit}
          >
            <NexusText variant="label" style={{ color: 'var(--nx-action-text)', fontWeight: 700 }}>
              {isProcessing ? 'Processing…' : isSettled ? 'Finalize & Spool Print' : `Settle (${currency} ${remaining} due)`}
            </NexusText>
          </NexusButton>
        </div>
      </div>
    </div>
  );
};
