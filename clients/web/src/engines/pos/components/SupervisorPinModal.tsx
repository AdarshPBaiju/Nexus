import React, { useState } from 'react';
import { NexusButton } from '@nexus/ui';

export interface SupervisorPinModalProps {
  readonly isOpen: boolean;
  readonly actionTitle: string;
  readonly onClose: () => void;
  readonly onAuthorize: (pin: string, reason: string) => void;
}

export const SupervisorPinModal: React.FC<SupervisorPinModalProps> = ({
  isOpen,
  actionTitle,
  onClose,
  onAuthorize,
}) => {
  const [pin, setPin] = useState('');
  const [reason, setReason] = useState('SUPERVISOR_AUTHORIZED');

  if (!isOpen) return null;

  const handleDigit = (digit: string) => {
    if (pin.length < 6) setPin((prev) => prev + digit);
  };

  const handleBackspace = () => {
    setPin((prev) => prev.slice(0, -1));
  };

  const handleConfirm = () => {
    if (pin.length >= 4) {
      onAuthorize(pin, reason);
      setPin('');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-sm rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-2xl">
        <h2 className="text-center text-lg font-bold text-[var(--nx-text-primary)]">Supervisor Authorization</h2>
        <p className="mt-1 text-center text-xs text-[var(--nx-text-secondary)]">{actionTitle}</p>

        <div className="my-4 flex justify-center">
          <input
            type="password"
            maxLength={6}
            readOnly
            value={pin}
            placeholder="••••"
            className="w-48 text-center font-mono text-2xl tracking-widest rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] py-2 text-[var(--nx-text-primary)]"
          />
        </div>

        {/* PIN keypad */}
        <div className="grid grid-cols-3 gap-2">
          {['1', '2', '3', '4', '5', '6', '7', '8', '9', 'C', '0', '⌫'].map((btn) => (
            <button
              key={btn}
              type="button"
              onClick={() => {
                if (btn === 'C') setPin('');
                else if (btn === '⌫') handleBackspace();
                else handleDigit(btn);
              }}
              className="flex h-12 items-center justify-center rounded-lg border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] text-lg font-bold text-[var(--nx-text-primary)] hover:bg-[var(--nx-border-subtle)] active:scale-95 transition-all"
            >
              {btn}
            </button>
          ))}
        </div>

        <div className="mt-4">
          <label className="block text-xs font-semibold text-[var(--nx-text-secondary)]">Audit Justification</label>
          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="mt-1 w-full rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] px-2 py-1.5 text-xs text-[var(--nx-text-primary)]"
          >
            <option value="CUSTOMER_SATISFACTION">Customer Satisfaction Comp</option>
            <option value="ORDERING_ERROR">Cashier / Barista Input Mistake</option>
            <option value="DEFECTIVE_PRODUCT">Product Quality Issue</option>
            <option value="MANAGER_DISCRETION">Manager Discretionary Courtesy</option>
          </select>
        </div>

        <div className="mt-6 flex justify-between gap-3">
          <NexusButton variant="secondary" onClick={onClose}>Cancel</NexusButton>
          <NexusButton variant="primary" onClick={handleConfirm} disabled={pin.length < 4}>Authorize</NexusButton>
        </div>
      </div>
    </div>
  );
};
