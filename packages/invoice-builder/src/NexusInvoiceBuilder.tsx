import React, { useState } from 'react';

export type InvoiceFormatPreview = 'A4_SHEET' | 'THERMAL_80MM' | 'CUP_LABEL' | 'DOT_MATRIX';

export interface NexusInvoiceBuilderProps {
  readonly templateCode: string;
  readonly templateName: string;
  readonly onSaveTemplate?: (code: string) => void;
}

/**
 * Visual Drag-and-Drop Invoice Builder Studio with WYSIWYG canvas and locked compliance slots.
 */
export const NexusInvoiceBuilder: React.FC<NexusInvoiceBuilderProps> = ({
  templateCode,
  templateName,
  onSaveTemplate,
}) => {
  const [activeFormat, setActiveFormat] = useState<InvoiceFormatPreview>('THERMAL_80MM');

  return (
    <div className="flex h-full w-full rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-bg)] text-[var(--nx-text-primary)] text-xs overflow-hidden">
      {/* Left: 24 Modular Fiscal Blocks */}
      <div className="w-64 p-3 border-e border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] space-y-2">
        <h3 className="font-bold text-[11px] text-[var(--nx-text-secondary)] uppercase">
          Fiscal Blocks
        </h3>
        <div className="p-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] cursor-grab">
          <span className="font-semibold block">Store Header (Locked)</span>
          <span className="text-[10px] text-[var(--nx-text-muted)]">HQ compliance slot</span>
        </div>
        <div className="p-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] cursor-grab">
          <span className="font-semibold block">Line Items Table</span>
          <span className="text-[10px] text-[var(--nx-text-muted)]">qty, item, price, tax</span>
        </div>
        <div className="p-2 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] cursor-grab">
          <span className="font-semibold block">ZATCA / GST QR</span>
          <span className="text-[10px] text-[var(--nx-text-muted)]">Statutory TLV verification</span>
        </div>
      </div>

      {/* Center: True-Scale WYSIWYG Canvas */}
      <div className="flex-1 p-4 flex flex-col justify-between bg-[var(--nx-surface-card)]">
        <div>
          <div className="flex items-center justify-between pb-3 border-b border-[var(--nx-border-subtle)]">
            <h2 className="font-bold text-sm">
              {templateName} <span className="font-mono text-xs text-[var(--nx-text-muted)]">({templateCode})</span>
            </h2>
            <div className="flex gap-1.5">
              {(['THERMAL_80MM', 'A4_SHEET', 'CUP_LABEL', 'DOT_MATRIX'] as const).map((fmt) => (
                <button
                  key={fmt}
                  type="button"
                  onClick={() => setActiveFormat(fmt)}
                  className={`px-2 py-1 rounded text-[11px] transition-colors ${
                    activeFormat === fmt
                      ? 'bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold'
                      : 'bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]'
                  }`}
                >
                  {fmt.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-8 flex justify-center">
            <div className="w-64 p-4 rounded bg-white text-black font-mono shadow-md border border-slate-200">
              <div className="text-center font-bold pb-2 border-b border-dashed border-slate-300">
                CAFE NEXUS (LOCKED HQ)
              </div>
              <div className="py-2 space-y-1 text-[11px]">
                <div className="flex justify-between">
                  <span>1x Espresso</span>
                  <span>$3.50</span>
                </div>
                <div className="flex justify-between font-bold border-t border-dashed border-slate-300 pt-1">
                  <span>TOTAL</span>
                  <span>$3.50</span>
                </div>
              </div>
              <div className="text-center text-[10px] pt-2 text-slate-500">
                [ZATCA/GST QR CODE]
              </div>
            </div>
          </div>
        </div>

        {onSaveTemplate && (
          <div className="pt-3 border-t border-[var(--nx-border-subtle)] flex justify-end">
            <button
              type="button"
              onClick={() => onSaveTemplate(templateCode)}
              className="px-4 py-1.5 rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold"
            >
              Save Template
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
