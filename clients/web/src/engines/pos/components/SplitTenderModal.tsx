import React, { useMemo, useState } from 'react';
import { NexusButton } from '@nexus/ui';
import type { SplitTenderEntry } from '../types';

export interface SplitTenderModalProps {
  readonly isOpen: boolean;
  readonly totalDue: string;
  readonly currency: string;
  readonly onClose: () => void;
  readonly onCompletePayment: (tenders: readonly SplitTenderEntry[]) => Promise<void>;
}

export const SplitTenderModal: React.FC<SplitTenderModalProps> = ({
  isOpen,
  totalDue,
  currency,
  onClose,
  onCompletePayment,
}) => {
  const due = parseFloat(totalDue) || 0;
  const [cashTendered, setCashTendered] = useState<string>('');
  const [cardAmount, setCardAmount] = useState<string>('');
  const [qrAmount, setQrAmount] = useState<string>('');

  const cashApplied = parseFloat(cashTendered) || 0;
  const cardApplied = parseFloat(cardAmount) || 0;
  const qrApplied = parseFloat(qrAmount) || 0;

  const totalApplied = useMemo(() => {
    return cardApplied + qrApplied + Math.min(cashApplied, Math.max(0, due - cardApplied - qrApplied));
  }, [cardApplied, qrApplied, cashApplied, due]);

  const changeDue = useMemo(() => {
    const cashPortion = Math.max(0, due - cardApplied - qrApplied);
    return Math.max(0, cashApplied - cashPortion).toFixed(2);
  }, [cardApplied, qrApplied, cashApplied, due]);

  const remaining = Math.max(0, due - totalApplied).toFixed(2);
  const isSettled = totalApplied >= due && due > 0;

  if (!isOpen) return null;

  const handleSubmit = async () => {
    if (!isSettled) return;
    const tenders: SplitTenderEntry[] = [];
    if (cashApplied > 0) {
      const applied = Math.min(cashApplied, Math.max(0, due - cardApplied - qrApplied));
      tenders.push({ tenderType: 'CASH', amount: applied.toFixed(2), tenderedAmount: cashApplied.toFixed(2), changeReturned: changeDue });
    }
    if (cardApplied > 0) {
      tenders.push({ tenderType: 'CARD', amount: cardApplied.toFixed(2), tenderedAmount: cardApplied.toFixed(2), changeReturned: '0.00' });
    }
    if (qrApplied > 0) {
      tenders.push({ tenderType: 'DIGITAL_QR', amount: qrApplied.toFixed(2), tenderedAmount: qrApplied.toFixed(2), changeReturned: '0.00' });
    }
    await onCompletePayment(tenders);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-4">
          <h2 className="text-lg font-bold text-[var(--nx-text-primary)]">Split Tender Checkout</h2>
          <button onClick={onClose} className="text-sm text-[var(--nx-text-muted)] hover:text-[var(--nx-text-primary)]" type="button">✕</button>
        </div>

        <div className="my-4 flex items-center justify-between rounded-lg bg-[var(--nx-surface-subtle)] p-4">
          <span className="text-sm font-medium text-[var(--nx-text-secondary)]">Total Amount Due:</span>
          <span className="font-mono text-2xl font-bold text-[var(--nx-text-primary)]">{currency} {totalDue}</span>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-[var(--nx-text-secondary)]">CASH TENDERED</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={cashTendered}
              onChange={(e) => setCashTendered(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-3 py-2 font-mono text-base text-[var(--nx-text-primary)]"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[var(--nx-text-secondary)]">CARD TERMINAL AMOUNT</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={cardAmount}
              onChange={(e) => setCardAmount(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-3 py-2 font-mono text-base text-[var(--nx-text-primary)]"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-[var(--nx-text-secondary)]">INSTANT QR (UPI / STRIPE)</label>
            <input
              type="number"
              step="0.01"
              placeholder="0.00"
              value={qrAmount}
              onChange={(e) => setQrAmount(e.target.value)}
              className="mt-1 w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-3 py-2 font-mono text-base text-[var(--nx-text-primary)]"
            />
          </div>
        </div>

        <div className="mt-6 flex justify-between border-t border-[var(--nx-border-subtle)] pt-4 text-sm font-semibold">
          <span className="text-[var(--nx-text-secondary)]">Change to Return:</span>
          <span className="font-mono text-base text-[var(--nx-status-success)]">{currency} {changeDue}</span>
        </div>
        <div className="mt-1 flex justify-between text-sm font-semibold">
          <span className="text-[var(--nx-text-secondary)]">Remaining Balance:</span>
          <span className="font-mono text-base text-[var(--nx-text-primary)]">{currency} {remaining}</span>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <NexusButton variant="secondary" onClick={onClose}>Cancel</NexusButton>
          <NexusButton variant="primary" onClick={handleSubmit} disabled={!isSettled}>Complete & Print Receipt</NexusButton>
        </div>
      </div>
    </div>
  );
};
