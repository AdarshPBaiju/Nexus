import React, { useState } from 'react';

export interface KeyInspectorDrawerProps {
  readonly isOpen: boolean;
  readonly keyPath: string;
  readonly defaultPattern: string;
  readonly currentTranslation: string;
  readonly description?: string;
  readonly onClose: () => void;
  readonly onSaveOverride?: (keyPath: string, newText: string) => void;
}

/**
 * In-Context Translation Key Inspector Drawer mounted via Shift + Alt + Click.
 * Strictly uses logical CSS classes (ms-*, me-*, ps-*, pe-*, text-start) for 100% RTL parity.
 */
export const KeyInspectorDrawer: React.FC<KeyInspectorDrawerProps> = ({
  isOpen,
  keyPath,
  defaultPattern,
  currentTranslation,
  description = '',
  onClose,
  onSaveOverride,
}) => {
  const [editedText, setEditedText] = useState(currentTranslation);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 end-0 z-50 w-80 md:w-96 border-s border-[var(--nx-border-default)] bg-[var(--nx-surface-elevated)] p-4 shadow-2xl flex flex-col justify-between text-start text-xs text-[var(--nx-text-primary)]">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[var(--nx-border-subtle)]">
          <div>
            <h3 className="font-bold text-sm">Key Inspector</h3>
            <span className="text-[10px] font-mono text-[var(--nx-text-muted)]">{keyPath}</span>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]"
            aria-label="Close Key Inspector"
          >
            ✕
          </button>
        </div>

        {/* Default ICU Pattern */}
        <div className="space-y-1">
          <label className="font-semibold text-[11px] text-[var(--nx-text-secondary)]">
            Default Pattern (ICU)
          </label>
          <div className="p-2 rounded bg-[var(--nx-surface-subtle)] font-mono text-[11px] text-[var(--nx-text-muted)] border border-[var(--nx-border-subtle)]">
            {defaultPattern}
          </div>
        </div>

        {/* Description Context */}
        {description && (
          <div className="space-y-1">
            <label className="font-semibold text-[11px] text-[var(--nx-text-secondary)]">
              Developer Context
            </label>
            <p className="text-[11px] text-[var(--nx-text-secondary)]">{description}</p>
          </div>
        )}

        {/* Inline Override Editor */}
        <div className="space-y-1">
          <label className="font-semibold text-[11px] text-[var(--nx-text-primary)]">
            Tenant Locale Override
          </label>
          <textarea
            rows={3}
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            className="w-full p-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--nx-border-focus)]"
          />
        </div>
      </div>

      {/* Footer Actions */}
      <div className="pt-3 border-t border-[var(--nx-border-subtle)] flex items-center justify-end gap-2">
        <button
          type="button"
          onClick={onClose}
          className="px-3 py-1.5 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]"
        >
          Cancel
        </button>
        {onSaveOverride && (
          <button
            type="button"
            onClick={() => onSaveOverride(keyPath, editedText)}
            className="px-3 py-1.5 rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold hover:opacity-90"
          >
            Save Override
          </button>
        )}
      </div>
    </div>
  );
};
