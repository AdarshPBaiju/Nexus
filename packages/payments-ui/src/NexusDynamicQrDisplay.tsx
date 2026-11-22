import React, { useState, useEffect } from 'react';

export interface NexusDynamicQrDisplayProps {
  readonly qrUri: string;
  readonly amount: string;
  readonly currency: string;
  readonly ttlSeconds?: number;
  readonly onExpired?: () => void;
}

/**
 * High-contrast dynamic QR canvas for customer-facing counter and station displays.
 */
export const NexusDynamicQrDisplay: React.FC<NexusDynamicQrDisplayProps> = ({
  qrUri,
  amount,
  currency,
  ttlSeconds = 180,
  onExpired,
}) => {
  const [secondsLeft, setSecondsLeft] = useState(ttlSeconds);

  useEffect(() => {
    if (secondsLeft <= 0) {
      onExpired?.();
      return;
    }
    const timer = setInterval(() => {
      setSecondsLeft((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [secondsLeft, onExpired]);

  const mins = Math.floor(secondsLeft / 60);
  const secs = secondsLeft % 60;
  const timeFormatted = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

  return (
    <div className="w-64 p-4 rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-center text-xs text-[var(--nx-text-primary)] shadow-md">
      <div className="p-3 bg-white rounded-lg border border-[var(--nx-border-subtle)] inline-block mb-3">
        {/* QR Placeholder / SVG Representation */}
        <div className="w-40 h-40 flex items-center justify-center font-mono text-[10px] text-black border-2 border-dashed border-slate-300 rounded">
          <span className="p-2 break-all">{qrUri.slice(0, 30)}...</span>
        </div>
      </div>

      <div className="font-bold text-sm font-mono nx-numeric mb-1">
        {currency} {amount}
      </div>
      <p className="text-[11px] text-[var(--nx-text-secondary)]">Scan with any UPI app to pay</p>

      <div className="mt-3 pt-2 border-t border-[var(--nx-border-subtle)] text-[10px] font-mono text-[var(--nx-text-muted)]">
        Expires in: <span className="font-semibold text-[var(--nx-status-warning)]">{timeFormatted}</span>
      </div>
    </div>
  );
};
