import React, { useState } from 'react';

export type PaymentMethodRail = 'CARD' | 'UPI_QR' | 'CASH';

export interface NexusPaymentModalProps {
  readonly isOpen: boolean;
  readonly amount: string;
  readonly currency: string;
  readonly onConfirmPayment?: (rail: PaymentMethodRail) => void;
  readonly onClose: () => void;
  readonly isProcessing?: boolean;
}

/**
 * PCI-DSS 4.0 compliant checkout modal with multi-rail tender selection.
 * Zero raw PAN: redirects to secure hosted elements, QR, or cash register.
 */
export const NexusPaymentModal: React.FC<NexusPaymentModalProps> = ({
  isOpen,
  amount,
  currency,
  onConfirmPayment,
  onClose,
  isProcessing = false,
}) => {
  const [selectedRail, setSelectedRail] = useState<PaymentMethodRail>('UPI_QR');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-elevated)] p-5 shadow-2xl text-[var(--nx-text-primary)] text-xs">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[var(--nx-border-subtle)]">
          <h2 className="font-bold text-sm">Checkout & Tender</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]"
            aria-label="Close Payment Modal"
          >
            ✕
          </button>
        </div>

        {/* Amount Display */}
        <div className="my-4 p-4 rounded text-center bg-[var(--nx-surface-subtle)] border border-[var(--nx-border-subtle)]">
          <span className="text-[11px] text-[var(--nx-text-secondary)] block">Total Due</span>
          <span className="text-xl font-bold font-mono nx-numeric text-[var(--nx-text-primary)]">
            {currency} {amount}
          </span>
        </div>

        {/* Payment Rails */}
        <div className="space-y-2 mb-5">
          <label className="font-semibold text-[11px] text-[var(--nx-text-secondary)] block">
            Select Payment Rail
          </label>
          {(['UPI_QR', 'CARD', 'CASH'] as const).map((rail) => (
            <button
              key={rail}
              type="button"
              onClick={() => setSelectedRail(rail)}
              className={`w-full p-2.5 rounded text-start flex items-center justify-between border transition-colors ${
                selectedRail === rail
                  ? 'border-[var(--nx-border-focus)] bg-[var(--nx-surface-selected)]/15 font-semibold text-[var(--nx-text-primary)]'
                  : 'border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-secondary)]'
              }`}
            >
              <span>{rail === 'UPI_QR' ? 'UPI Dynamic QR' : rail === 'CARD' ? 'Card Terminal' : 'Cash Drawer'}</span>
              <span className="text-[10px] text-[var(--nx-text-muted)]">
                {rail === 'UPI_QR' ? '0% MDR' : rail === 'CARD' ? 'Instant' : 'Counter'}
              </span>
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-[var(--nx-border-subtle)]">
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1.5 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-secondary)]"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onConfirmPayment?.(selectedRail)}
            disabled={isProcessing}
            className="px-4 py-1.5 rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold hover:opacity-90 disabled:opacity-50"
          >
            {isProcessing ? 'Processing...' : 'Pay Now'}
          </button>
        </div>
      </div>
    </div>
  );
};
