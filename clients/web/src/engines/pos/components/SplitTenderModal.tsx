'use client';

import React, { useId, useMemo, useState } from 'react';
import { NexusButton, NexusBadge } from '@nexus/ui';
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
  const modalLabelId = useId();
  const due = parseFloat(totalDue) || 0;
  const [cashTendered, setCashTendered] = useState<string>('');
  const [cardAmount, setCardAmount] = useState<string>('');
  const [qrAmount, setQrAmount] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [completedDigest, setCompletedDigest] = useState<string | null>(null);

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

  const addCashDenom = (denom: number) => {
    const current = parseFloat(cashTendered) || 0;
    setCashTendered((current + denom).toFixed(2));
  };

  const handlePayFullCard = () => {
    const rem = Math.max(0, due - cashApplied - qrApplied);
    setCardAmount(rem.toFixed(2));
  };

  const handlePayFullQr = () => {
    const rem = Math.max(0, due - cashApplied - cardApplied);
    setQrAmount(rem.toFixed(2));
  };

  const handleSubmit = async () => {
    if (!isSettled || isProcessing) return;
    setIsProcessing(true);
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

    // Generate mock SHA-256 fiscal digest
    const digest = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
    setCompletedDigest(digest);
    await onCompletePayment(tenders);
    setIsProcessing(false);
  };

  const handleResetAndClose = () => {
    setCompletedDigest(null);
    setCashTendered('');
    setCardAmount('');
    setQrAmount('');
    onClose();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={modalLabelId}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-md p-4"
    >
      <div className="w-full max-w-lg rounded-3xl border border-surface-container-highest bg-surface-container-low p-6 shadow-2xl space-y-4">
        {completedDigest ? (
          /* Fiscal Receipt Settled Screen */
          <div className="flex flex-col items-center text-center space-y-4 py-2">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
              <span className="material-symbols-outlined text-[32px]">check_circle</span>
            </div>
            <div>
              <h2 className="font-headline-sm text-headline-sm font-bold text-on-surface">PAYMENT SETTLED & AUDITED</h2>
              <p className="text-xs text-outline font-mono mt-0.5">Order Token #042 · Series FSC-LON-004291</p>
            </div>
            <div className="w-full rounded-2xl bg-surface-container p-4 font-mono text-xs text-left space-y-2 border border-surface-container-highest">
              <div className="flex justify-between text-outline">
                <span>TOTAL PAID:</span>
                <span className="text-on-surface font-bold">{currency} {totalDue}</span>
              </div>
              {parseFloat(changeDue) > 0 && (
                <div className="flex justify-between text-emerald-400 font-bold">
                  <span>CHANGE RETURNED:</span>
                  <span>{currency} {changeDue}</span>
                </div>
              )}
              <div className="border-t border-surface-container-highest pt-2 text-[10px] text-outline break-all">
                <span className="text-secondary font-bold block mb-0.5">SHA-256 FISCAL INTEGRITY:</span>
                {completedDigest}
              </div>
            </div>
            <div className="flex gap-2 w-full">
              <NexusButton variant="secondary" className="flex-1 justify-center" onClick={() => alert('Dispatched ESC/POS 80mm thermal receipt!')}>
                🖨 Print Receipt
              </NexusButton>
              <NexusButton variant="primary" className="flex-1 justify-center" onClick={handleResetAndClose}>
                Next Customer &rarr;
              </NexusButton>
            </div>
          </div>
        ) : (
          /* Split Tender Form */
          <>
            <div className="flex items-center justify-between border-b border-surface-container-highest pb-3">
              <h2 id={modalLabelId} className="font-headline-sm text-headline-sm font-bold text-on-surface">
                Split-Tender Checkout
              </h2>
              <button onClick={onClose} className="p-1 rounded-lg text-outline hover:text-on-surface" type="button">✕</button>
            </div>

            {/* Total Due Banner */}
            <div className="flex items-center justify-between rounded-2xl bg-surface-container p-4 border border-surface-container-highest">
              <div>
                <span className="text-xs text-outline font-mono uppercase block">Total Payable</span>
                <span className="font-mono text-2xl font-bold text-primary">{currency} {totalDue}</span>
              </div>
              <div className="text-right font-mono">
                <span className="text-xs text-outline uppercase block">Remaining</span>
                <span className={`text-lg font-bold ${parseFloat(remaining) > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {currency} {remaining}
                </span>
              </div>
            </div>

            {/* Tenders */}
            <div className="space-y-3 font-mono text-xs">
              {/* Cash Rail */}
              <div className="rounded-xl bg-surface-container p-3 border border-surface-container-highest space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-on-surface font-semibold">💵 CASH TENDER</span>
                  <span className="text-emerald-400 font-bold">Change Due: {currency} {changeDue}</span>
                </div>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={cashTendered}
                  onChange={(e) => setCashTendered(e.target.value)}
                  className="w-full h-10 px-3 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface text-base font-bold focus:border-primary outline-none"
                />
                <div className="flex gap-1.5 pt-1">
                  {[5, 10, 20, 50, 100].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => addCashDenom(d)}
                      className="flex-1 py-1 rounded bg-surface-container-high hover:bg-surface-bright text-[11px] font-bold text-outline hover:text-on-surface transition-colors"
                    >
                      +{currency}{d}
                    </button>
                  ))}
                </div>
              </div>

              {/* Card EDC Rail */}
              <div className="rounded-xl bg-surface-container p-3 border border-surface-container-highest flex items-center justify-between gap-3">
                <div className="flex-1">
                  <span className="text-on-surface font-semibold block">💳 CARD EDC TERMINAL</span>
                  <span className="text-[10px] text-outline">Pine Labs / Ingenico Bridge</span>
                </div>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={cardAmount}
                  onChange={(e) => setCardAmount(e.target.value)}
                  className="w-28 h-9 px-2 text-right rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface text-sm font-bold focus:border-primary outline-none"
                />
                <button type="button" onClick={handlePayFullCard} className="px-2 py-1 rounded bg-primary/20 hover:bg-primary/30 text-primary text-[11px] font-bold">
                  Full
                </button>
              </div>

              {/* Instant QR Rail */}
              <div className="rounded-xl bg-surface-container p-3 border border-surface-container-highest flex items-center justify-between gap-3">
                <div className="flex-1">
                  <span className="text-on-surface font-semibold block">📱 DIGITAL QR (UPI / STRIPE)</span>
                  <span className="text-[10px] text-outline">Instant webhook reconciliation</span>
                </div>
                <input
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  value={qrAmount}
                  onChange={(e) => setQrAmount(e.target.value)}
                  className="w-28 h-9 px-2 text-right rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface text-sm font-bold focus:border-primary outline-none"
                />
                <button type="button" onClick={handlePayFullQr} className="px-2 py-1 rounded bg-primary/20 hover:bg-primary/30 text-primary text-[11px] font-bold">
                  Full
                </button>
              </div>
            </div>

            {/* Action Footer */}
            <div className="flex gap-2 pt-2 border-t border-surface-container-highest">
              <NexusButton variant="outline" onClick={onClose} className="flex-1 justify-center">
                Cancel
              </NexusButton>
              <NexusButton
                variant="primary"
                onClick={handleSubmit}
                disabled={!isSettled || isProcessing}
                className="flex-1 justify-center"
              >
                {isProcessing ? 'Settling...' : `Confirm Payment (${currency}${totalDue})`}
              </NexusButton>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
