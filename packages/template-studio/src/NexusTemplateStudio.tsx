import React, { useState } from 'react';

export type TemplateTargetPreview = 'EMAIL' | 'WHATSAPP' | 'THERMAL_80MM' | 'A4_PDF';

export interface NexusTemplateStudioProps {
  readonly templateCode: string;
  readonly templateName: string;
  readonly isSystemLocked?: boolean;
  readonly onSave?: (code: string) => void;
}

/**
 * Visual Template Studio split workspace with multi-target live device preview.
 */
export const NexusTemplateStudio: React.FC<NexusTemplateStudioProps> = ({
  templateCode,
  templateName,
  isSystemLocked = false,
  onSave,
}) => {
  const [activeTarget, setActiveTarget] = useState<TemplateTargetPreview>('THERMAL_80MM');

  return (
    <div className="flex h-full w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-bg)] text-[var(--nx-text-primary)] overflow-hidden">
      {/* Left Canvas: AST Node Structure & Locks */}
      <div className="w-1/2 p-4 border-r border-[var(--nx-border-subtle)] flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-[var(--nx-border-subtle)]">
            <div>
              <h2 className="text-sm font-bold">{templateName}</h2>
              <span className="text-xs text-[var(--nx-text-muted)] font-mono">{templateCode}</span>
            </div>
            {isSystemLocked && (
              <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-[var(--nx-status-warning)]/10 text-[var(--nx-status-warning)] border border-[var(--nx-status-warning)]/30">
                HQ LOCKED
              </span>
            )}
          </div>
          <div className="mt-4 space-y-2 text-xs">
            <div className="p-2 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-card)]">
              <span className="font-semibold text-[var(--nx-text-primary)]">Header Slot</span>
              <p className="text-[var(--nx-text-secondary)]">Store Name & Tax ID (Locked)</p>
            </div>
            <div className="p-2 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-card)]">
              <span className="font-semibold text-[var(--nx-text-primary)]">Line Items Loop</span>
              <p className="text-[var(--nx-text-secondary)]">item.name, item.qty, item.total</p>
            </div>
            <div className="p-2 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-card)]">
              <span className="font-semibold text-[var(--nx-text-primary)]">QR / Barcode Slot</span>
              <p className="text-[var(--nx-text-secondary)]">ZATCA / GST e-Invoice QR Code</p>
            </div>
          </div>
        </div>

        {onSave && (
          <button
            type="button"
            onClick={() => onSave(templateCode)}
            className="w-full py-2 text-xs font-semibold rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] hover:opacity-90"
          >
            Save Template
          </button>
        )}
      </div>

      {/* Right Canvas: Multi-Target Live Preview */}
      <div className="w-1/2 p-4 flex flex-col bg-[var(--nx-surface-subtle)]">
        <div className="flex gap-2 pb-3 border-b border-[var(--nx-border-subtle)]">
          {(['THERMAL_80MM', 'A4_PDF', 'EMAIL', 'WHATSAPP'] as const).map((target) => (
            <button
              key={target}
              type="button"
              onClick={() => setActiveTarget(target)}
              className={`px-2.5 py-1 text-xs rounded transition-colors ${
                activeTarget === target
                  ? 'bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-medium'
                  : 'bg-[var(--nx-surface-card)] text-[var(--nx-text-secondary)] border border-[var(--nx-border-default)]'
              }`}
            >
              {target.replace('_', ' ')}
            </button>
          ))}
        </div>
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-xs p-4 rounded bg-[var(--nx-surface-card)] border border-[var(--nx-border-default)] shadow-sm text-center font-mono text-xs">
            <p className="font-bold border-b border-dashed pb-2 mb-2">*** PROJECT NEXUS ***</p>
            <p>1x Flat White - $4.50</p>
            <p>1x Croissant - $3.50</p>
            <p className="border-t border-dashed pt-2 mt-2 font-bold">TOTAL: $8.00</p>
            <p className="text-[10px] text-[var(--nx-text-muted)] mt-2">Target: {activeTarget}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
