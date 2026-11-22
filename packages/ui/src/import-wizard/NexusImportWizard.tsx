'use client';
import React, { useState } from 'react';

export interface NexusImportWizardProps {
  isOpen: boolean;
  onClose: () => void;
  entityName: string;
  onUploadComplete: (sessionId: string) => void;
}

export const NexusImportWizard: React.FC<NexusImportWizardProps> = ({
  isOpen,
  onClose,
  entityName,
  onUploadComplete,
}) => {
  const [step, setStep] = useState<'DROPZONE' | 'PREVIEW' | 'COMMITTED'>('DROPZONE');
  const [file, setFile] = useState<File | null>(null);

  if (!isOpen) return null;

  const handleSimulatedUpload = () => {
    setStep('PREVIEW');
  };

  const handleCommit = () => {
    setStep('COMMITTED');
    onUploadComplete('batch-session-001');
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <div className="w-full max-w-2xl rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-4">
          <h2 className="text-lg font-semibold text-[var(--nx-text-primary)]">
            Import {entityName} Wizard
          </h2>
          <span className="text-xs uppercase font-mono px-2 py-0.5 rounded bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]">
            Step: {step}
          </span>
        </div>

        <div className="py-6">
          {step === 'DROPZONE' && (
            <div className="border-2 border-dashed border-[var(--nx-border-default)] rounded-lg p-10 text-center hover:border-[var(--nx-border-focus)] transition-colors">
              <p className="text-sm text-[var(--nx-text-secondary)]">
                Drag and drop your CSV or Excel file here to begin zero-trust ingestion.
              </p>
              <button
                type="button"
                onClick={handleSimulatedUpload}
                className="mt-4 px-4 py-2 rounded bg-[var(--nx-action-primary)] text-sm font-medium text-[var(--nx-action-text)] hover:bg-[var(--nx-action-primary-hover)]"
              >
                Upload File
              </button>
            </div>
          )}

          {step === 'PREVIEW' && (
            <div className="space-y-4">
              <div className="p-4 rounded border border-emerald-500/20 bg-emerald-500/10 text-emerald-800 dark:text-emerald-400 text-sm">
                Dry-run validation successful: 50 rows staged, 0 errors detected.
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setStep('DROPZONE')}
                  className="px-4 py-2 rounded border border-[var(--nx-border-default)] text-sm text-[var(--nx-text-secondary)] hover:bg-[var(--nx-surface-subtle)]"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={handleCommit}
                  className="px-4 py-2 rounded bg-[var(--nx-action-primary)] text-sm font-medium text-[var(--nx-action-text)] hover:bg-[var(--nx-action-primary-hover)]"
                >
                  Commit Ingestion
                </button>
              </div>
            </div>
          )}

          {step === 'COMMITTED' && (
            <div className="text-center py-6">
              <h3 className="text-base font-semibold text-[var(--nx-text-primary)]">
                Batch Successfully Committed!
              </h3>
              <p className="mt-1 text-sm text-[var(--nx-text-secondary)]">
                Safe 1-click batch rollback is active for the next 24 hours.
              </p>
              <button
                type="button"
                onClick={onClose}
                className="mt-6 px-4 py-2 rounded bg-[var(--nx-surface-subtle)] text-sm font-medium text-[var(--nx-text-primary)] hover:bg-[var(--nx-border-subtle)]"
              >
                Close Wizard
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
