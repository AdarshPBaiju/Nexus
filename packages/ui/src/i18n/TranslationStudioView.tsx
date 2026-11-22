'use client';
import React, { useState } from 'react';

export interface TranslationRow {
  readonly key: string;
  readonly defaultText: string;
  readonly translatedText: string;
  readonly status: 'APPROVED' | 'MACHINE' | 'MISSING';
}

export interface TranslationStudioViewProps {
  readonly namespaces: readonly string[];
  readonly rows: readonly TranslationRow[];
  readonly onAutoTranslate?: (ns: string) => void;
  readonly onPublishBundle?: () => void;
}

/**
 * Web Translation Studio mounted at /owner/i18n.
 * Adheres strictly to logical CSS rules and dual-mode theme parity.
 */
export const TranslationStudioView: React.FC<TranslationStudioViewProps> = ({
  namespaces,
  rows,
  onAutoTranslate,
  onPublishBundle,
}) => {
  const [selectedNs, setSelectedNs] = useState(namespaces[0] || 'core');

  return (
    <div className="flex h-full w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-bg)] text-start text-xs text-[var(--nx-text-primary)] overflow-hidden">
      {/* Left Pane: Namespace Selector */}
      <div className="w-56 p-3 border-e border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] space-y-1">
        <h3 className="font-bold text-[11px] text-[var(--nx-text-secondary)] uppercase ps-2 pb-2">
          Namespaces
        </h3>
        {namespaces.map((ns) => (
          <button
            key={ns}
            type="button"
            onClick={() => setSelectedNs(ns)}
            className={`w-full text-start px-2.5 py-1.5 rounded text-xs transition-colors ${
              selectedNs === ns
                ? 'bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold'
                : 'text-[var(--nx-text-secondary)] hover:bg-[var(--nx-surface-card)]'
            }`}
          >
            {ns}
          </button>
        ))}
      </div>

      {/* Right Pane: Translation Table & Actions */}
      <div className="flex-1 p-4 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-[var(--nx-border-subtle)]">
            <h2 className="text-sm font-bold">
              Namespace: <span className="font-mono">{selectedNs}</span>
            </h2>
            <div className="flex items-center gap-2">
              {onAutoTranslate && (
                <button
                  type="button"
                  onClick={() => onAutoTranslate(selectedNs)}
                  className="px-2.5 py-1 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]"
                >
                  Auto-Translate
                </button>
              )}
              {onPublishBundle && (
                <button
                  type="button"
                  onClick={onPublishBundle}
                  className="px-2.5 py-1 rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold hover:opacity-90"
                >
                  Publish Bundle
                </button>
              )}
            </div>
          </div>

          {/* Table */}
          <div className="mt-4 divide-y divide-[var(--nx-border-subtle)]">
            {rows.map((row) => (
              <div key={row.key} className="py-2.5 flex items-center justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <span className="font-mono text-[10px] text-[var(--nx-text-muted)] block">
                    {row.key}
                  </span>
                  <span className="font-medium text-xs block text-[var(--nx-text-primary)]">
                    {row.translatedText || row.defaultText}
                  </span>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                    row.status === 'APPROVED'
                      ? 'bg-[var(--nx-status-success)]/10 text-[var(--nx-status-success)]'
                      : row.status === 'MACHINE'
                        ? 'bg-[var(--nx-status-warning)]/10 text-[var(--nx-status-warning)]'
                        : 'bg-[var(--nx-status-danger)]/10 text-[var(--nx-status-danger)]'
                  }`}
                >
                  {row.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
