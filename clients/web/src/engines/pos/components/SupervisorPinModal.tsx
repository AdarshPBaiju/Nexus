import React, { useState } from 'react';
import { NexusButton, NexusSelect, NexusText } from '@nexus/ui';

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
  const [reason, setReason] = useState('MANAGER_DISCRETION');

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
        <NexusText variant="h3" style={{ textAlign: 'center' }}>Supervisor Authorization</NexusText>
        <NexusText variant="caption" role="muted" style={{ textAlign: 'center', marginTop: '4px' }}>
          {actionTitle}
        </NexusText>

        <div className="my-4 flex justify-center gap-2">
          {[0, 1, 2, 3].map((idx) => {
            const filled = idx < pin.length;
            return (
              <span
                key={idx}
                aria-hidden="true"
                style={{
                  width: '14px',
                  height: '14px',
                  borderRadius: '9999px',
                  border: `2px solid ${filled ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                  backgroundColor: filled ? 'var(--nx-action-primary)' : 'transparent',
                  transition: 'background-color 0.12s ease',
                }}
              />
            );
          })}
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
          <NexusText variant="caption" role="secondary" style={{ display: 'block', marginBottom: '4px' }}>
            Audit Justification
          </NexusText>
          <NexusSelect
            value={reason}
            onChange={setReason}
            options={[
              { value: 'CUSTOMER_SATISFACTION', label: 'Customer Satisfaction Comp' },
              { value: 'ORDERING_ERROR', label: 'Cashier / Barista Input Mistake' },
              { value: 'DEFECTIVE_PRODUCT', label: 'Product Quality Issue' },
              { value: 'MANAGER_DISCRETION', label: 'Manager Discretionary Courtesy' },
            ]}
          />
        </div>

        <div className="mt-6 flex justify-between gap-3">
          <NexusButton variant="secondary" onClick={onClose}>Cancel</NexusButton>
          <NexusButton variant="primary" onClick={handleConfirm} disabled={pin.length < 4}>Authorize</NexusButton>
        </div>
      </div>
    </div>
  );
};
