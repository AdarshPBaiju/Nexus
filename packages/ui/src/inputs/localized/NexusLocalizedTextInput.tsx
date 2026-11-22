import React, { useState } from 'react';

export type TranslationCoverageStatus = 'COMPLETE' | 'MACHINE' | 'MISSING';

export interface NexusLocalizedTextInputProps {
  readonly label: string;
  readonly activeLocale: string;
  readonly values: Record<string, string>;
  readonly coverageStatus?: TranslationCoverageStatus;
  readonly onChange?: (locale: string, value: string) => void;
  readonly onReTranslate?: () => void;
  readonly isTranslating?: boolean;
}

/**
 * Custom Input Primitive #19: Multilingual Localized Text Input with live coverage indicator.
 */
export const NexusLocalizedTextInput: React.FC<NexusLocalizedTextInputProps> = ({
  label,
  activeLocale,
  values,
  coverageStatus = 'COMPLETE',
  onChange,
  onReTranslate,
  isTranslating = false,
}) => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const currentValue = values[activeLocale] || '';

  const getStatusBadge = () => {
    switch (coverageStatus) {
      case 'COMPLETE':
        return <span className="h-2 w-2 rounded-full bg-[var(--nx-status-success)]" title="Human Verified" />;
      case 'MACHINE':
        return <span className="h-2 w-2 rounded-full bg-[var(--nx-status-warning)]" title="Machine Translated" />;
      case 'MISSING':
        return <span className="h-2 w-2 rounded-full bg-[var(--nx-status-danger)]" title="Missing Locales" />;
    }
  };

  return (
    <div className="w-full space-y-1.5 text-xs text-[var(--nx-text-primary)]">
      <div className="flex items-center justify-between">
        <label className="font-medium flex items-center gap-1.5">
          <span>{label}</span>
          {getStatusBadge()}
        </label>
        <div className="flex items-center gap-2">
          {onReTranslate && (
            <button
              type="button"
              onClick={onReTranslate}
              disabled={isTranslating}
              className="text-[10px] text-[var(--nx-action-primary)] hover:underline disabled:opacity-50"
            >
              {isTranslating ? 'Translating...' : 'Re-translate'}
            </button>
          )}
          <button
            type="button"
            onClick={() => setIsDrawerOpen((prev) => !prev)}
            className="text-[10px] text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]"
          >
            {isDrawerOpen ? 'Close Drawer' : `Languages (${Object.keys(values).length})`}
          </button>
        </div>
      </div>

      {/* Primary Active Input */}
      <div className="relative">
        <input
          type="text"
          value={currentValue}
          onChange={(e) => onChange?.(activeLocale, e.target.value)}
          className="w-full px-3 py-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--nx-border-focus)] transition-colors"
          placeholder={`Enter ${label} in ${activeLocale}`}
        />
        <span className="absolute right-2.5 top-2.5 text-[10px] font-mono text-[var(--nx-text-muted)] uppercase">
          {activeLocale}
        </span>
      </div>

      {/* Multi-Language Parallel Drawer */}
      {isDrawerOpen && (
        <div className="mt-2 p-3 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] space-y-2">
          <p className="text-[11px] font-semibold text-[var(--nx-text-secondary)]">
            Parallel Translations
          </p>
          {Object.entries(values).map(([loc, val]) => (
            <div key={loc} className="flex items-center gap-2">
              <span className="w-14 font-mono text-[10px] text-[var(--nx-text-muted)] uppercase">
                {loc}
              </span>
              <input
                type="text"
                value={val}
                onChange={(e) => onChange?.(loc, e.target.value)}
                className="flex-1 px-2 py-1 text-xs rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-primary)]"
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
