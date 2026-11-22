import React from 'react';

export interface AuditDiffField {
  fieldName: string;
  before: unknown;
  after: unknown;
}

export interface AuditDiffDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  entityName: string;
  recordId: string;
  changedFields: Record<string, { before: unknown; after: unknown }>;
}

export const AuditDiffDrawer: React.FC<AuditDiffDrawerProps> = ({
  isOpen,
  onClose,
  entityName,
  recordId,
  changedFields,
}) => {
  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm"
    >
      <div className="w-full max-w-xl h-full bg-[var(--nx-surface-card)] border-s border-[var(--nx-border-default)] shadow-2xl flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-[var(--nx-border-subtle)]">
          <div>
            <h2 className="text-lg font-semibold text-[var(--nx-text-primary)]">
              Audit Diff: {entityName}
            </h2>
            <p className="text-xs text-[var(--nx-text-secondary)] font-mono">{recordId}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="px-3 py-1 rounded bg-[var(--nx-surface-subtle)] text-[var(--nx-text-primary)] hover:bg-[var(--nx-border-subtle)] text-sm"
          >
            Close
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {Object.keys(changedFields).length === 0 ? (
            <p className="text-sm text-[var(--nx-text-muted)] italic">No modified fields detected.</p>
          ) : (
            Object.entries(changedFields).map(([field, delta]) => (
              <div
                key={field}
                className="rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] p-3"
              >
                <div className="text-xs font-semibold uppercase tracking-wider text-[var(--nx-text-secondary)] mb-2">
                  {field}
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20">
                    <span className="block font-bold mb-1">- Before:</span>
                    <pre className="whitespace-pre-wrap break-all">{JSON.stringify(delta.before, null, 2)}</pre>
                  </div>
                  <div className="p-2 rounded bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20">
                    <span className="block font-bold mb-1">+ After:</span>
                    <pre className="whitespace-pre-wrap break-all">{JSON.stringify(delta.after, null, 2)}</pre>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
