import React, { useState } from 'react';

export interface SensitiveFieldMaskProps {
  readonly value: string;
  readonly maskPattern?: string;
  readonly onRevealAudit?: () => void;
}

/**
 * Displays masked sensitive string (****1234) with audited break-glass 1-click reveal.
 * Strict semantic --nx-* token styling satisfying WCAG 2.2 AA in both light & dark modes.
 */
export const SensitiveFieldMask: React.FC<SensitiveFieldMaskProps> = ({
  value,
  maskPattern = '************',
  onRevealAudit,
}) => {
  const [isRevealed, setIsRevealed] = useState(false);

  const handleToggle = () => {
    if (!isRevealed && onRevealAudit) {
      onRevealAudit();
    }
    setIsRevealed((prev) => !prev);
  };

  const maskedText = value.length > 4 ? `${maskPattern}${value.slice(-4)}` : maskPattern;

  return (
    <span className="inline-flex items-center gap-2 font-mono text-sm nx-numeric text-[var(--nx-text-primary)]">
      <span>{isRevealed ? value : maskedText}</span>
      <button
        type="button"
        onClick={handleToggle}
        className="px-1.5 py-0.5 text-xs rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)] hover:bg-[var(--nx-surface-elevated)] hover:text-[var(--nx-text-primary)] transition-colors focus:outline-none focus:ring-1 focus:ring-[var(--nx-border-focus)]"
        aria-label={isRevealed ? 'Hide sensitive value' : 'Reveal sensitive value'}
      >
        {isRevealed ? 'Hide' : 'Reveal'}
      </button>
    </span>
  );
};
