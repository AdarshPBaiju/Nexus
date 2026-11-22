import React from 'react';

export interface CalibrationPoint {
  readonly field: string;
  readonly xMm: number;
  readonly yMm: number;
}

export interface StationeryCalibrationCanvasProps {
  readonly points: readonly CalibrationPoint[];
  readonly onPointMoved?: (field: string, newX: number, newY: number) => void;
}

/**
 * Visual canvas for calibrating print coordinates onto pre-printed stationery forms (±0.1mm).
 */
export const StationeryCalibrationCanvas: React.FC<StationeryCalibrationCanvasProps> = ({
  points,
  onPointMoved,
}) => {
  return (
    <div className="w-full h-80 rounded border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-4 relative font-mono text-xs">
      <div className="text-[11px] text-[var(--nx-text-muted)] mb-2">
        Pre-Printed Stationery Calibration Grid (1mm per notch)
      </div>
      <div className="w-full h-64 border border-dashed border-[var(--nx-border-subtle)] relative bg-[var(--nx-surface-subtle)]/50">
        {points.map((p) => (
          <div
            key={p.field}
            style={{ left: `${p.xMm * 2}px`, top: `${p.yMm * 2}px` }}
            className="absolute px-1.5 py-0.5 rounded bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] text-[10px] cursor-move select-none"
            title={`${p.field}: (${p.xMm}mm, ${p.yMm}mm)`}
          >
            {p.field}
          </div>
        ))}
      </div>
    </div>
  );
};
