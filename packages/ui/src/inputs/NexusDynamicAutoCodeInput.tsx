import React, { useState } from 'react';

export interface NexusDynamicAutoCodeInputProps {
  label: string;
  previewCode: string;
  allowManualOverride?: boolean;
  value?: string;
  onChange?: (val: string) => void;
  helperText?: string;
}

export const NexusDynamicAutoCodeInput: React.FC<NexusDynamicAutoCodeInputProps> = ({
  label,
  previewCode,
  allowManualOverride = false,
  value,
  onChange,
  helperText,
}) => {
  const [isManual, setIsManual] = useState(false);

  return (
    <div className="flex flex-col space-y-1 font-sans">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-[var(--nx-text-primary)]">
          {label}
        </label>
        {allowManualOverride && (
          <button
            type="button"
            onClick={() => setIsManual(!isManual)}
            className="text-xs text-[var(--nx-action-primary)] hover:underline"
          >
            {isManual ? 'Use Auto Sequence' : 'Manual Override'}
          </button>
        )}
      </div>

      {isManual ? (
        <input
          type="text"
          value={value ?? ''}
          onChange={(e) => onChange?.(e.target.value)}
          className="px-3 py-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-primary)] font-mono text-sm focus:border-[var(--nx-border-focus)] outline-none"
        />
      ) : (
        <div className="flex items-center justify-between px-3 py-2 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] text-[var(--nx-text-primary)] font-mono text-sm">
          <span>{previewCode}</span>
          <span className="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-700 dark:text-blue-400">
            Auto-Generated
          </span>
        </div>
      )}

      {helperText && (
        <p className="text-xs text-[var(--nx-text-secondary)]">{helperText}</p>
      )}
    </div>
  );
};
