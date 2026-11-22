import React, { useState } from 'react';

export interface NexusExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  entityName: string;
  totalRowCount: number;
  onConfirmExport: (format: 'CSV' | 'XLSX' | 'PARQUET') => void;
}

export const NexusExportModal: React.FC<NexusExportModalProps> = ({
  isOpen,
  onClose,
  entityName,
  totalRowCount,
  onConfirmExport,
}) => {
  const [format, setFormat] = useState<'CSV' | 'XLSX' | 'PARQUET'>('CSV');

  if (!isOpen) return null;

  const isAsync = totalRowCount > 1000;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <div className="w-full max-w-md rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-xl">
        <h3 className="text-lg font-semibold text-[var(--nx-text-primary)]">
          Export {entityName}
        </h3>
        <p className="mt-1 text-sm text-[var(--nx-text-secondary)]">
          {totalRowCount.toLocaleString()} rows selected.
          {isAsync && (
            <span className="block mt-1 font-medium text-amber-600 dark:text-amber-400">
              Large export lane: file will be streamed asynchronously.
            </span>
          )}
        </p>

        <div className="mt-4 space-y-2">
          {(['CSV', 'XLSX', 'PARQUET'] as const).map((fmt) => (
            <label
              key={fmt}
              className={`flex items-center justify-between p-3 rounded border cursor-pointer ${
                format === fmt
                  ? 'border-[var(--nx-border-focus)] bg-[var(--nx-surface-subtle)]'
                  : 'border-[var(--nx-border-subtle)]'
              }`}
            >
              <span className="text-sm font-medium text-[var(--nx-text-primary)]">{fmt}</span>
              <input
                type="radio"
                name="exportFormat"
                value={fmt}
                checked={format === fmt}
                onChange={() => setFormat(fmt)}
                className="accent-[var(--nx-action-primary)]"
              />
            </label>
          ))}
        </div>

        <div className="mt-6 flex justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded border border-[var(--nx-border-default)] text-sm text-[var(--nx-text-secondary)] hover:bg-[var(--nx-surface-subtle)]"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onConfirmExport(format)}
            className="px-4 py-2 rounded bg-[var(--nx-action-primary)] text-sm font-medium text-[var(--nx-action-text)] hover:bg-[var(--nx-action-primary-hover)]"
          >
            Start Export
          </button>
        </div>
      </div>
    </div>
  );
};
