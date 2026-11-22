import React, { useState } from 'react';
import { NexusBadge, NexusButton } from '@nexus/ui';
import type { AttendanceRecordDto, ClockInMethod } from './types';

export interface EssPunchClockWidgetProps {
  readonly employeeId: string;
  readonly branchId: string;
  readonly activePunch?: AttendanceRecordDto | null;
  readonly onClockIn: (method: ClockInMethod) => Promise<void>;
  readonly onClockOut: () => Promise<void>;
}

export const EssPunchClockWidget: React.FC<EssPunchClockWidgetProps> = ({
  activePunch,
  onClockIn,
  onClockOut,
}) => {
  const [loading, setLoading] = useState(false);
  const isClockedIn = Boolean(activePunch && !activePunch.clockOutUtc);

  const handlePunch = async () => {
    setLoading(true);
    try {
      if (isClockedIn) {
        await onClockOut();
      } else {
        await onClockIn('WEB');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-6 shadow-md">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-semibold text-[var(--nx-text-secondary)]">EMPLOYEE SELF-SERVICE</span>
          <h2 className="text-lg font-bold text-[var(--nx-text-primary)]">Attendance Punch Clock</h2>
        </div>
        <NexusBadge variant={isClockedIn ? 'success' : 'neutral'}>
          {isClockedIn ? 'ON DUTY' : 'OFF DUTY'}
        </NexusBadge>
      </div>

      <div className="my-6 rounded-xl bg-[var(--nx-surface-subtle)] p-4 text-center">
        <div className="text-xs text-[var(--nx-text-muted)]">ACTIVE BUSINESS DATE</div>
        <div className="mt-1 font-mono text-xl font-bold text-[var(--nx-text-primary)]">
          {activePunch?.businessDate ?? new Date().toISOString().split('T')[0]}
        </div>
        {isClockedIn && (
          <div className="mt-2 text-xs text-[var(--nx-text-secondary)]">
            Clocked in at: <span className="font-mono">{activePunch?.clockInUtc}</span>
          </div>
        )}
      </div>

      <div className="flex justify-center">
        <NexusButton
          variant={isClockedIn ? 'danger' : 'primary'}
          size="lg"
          onClick={handlePunch}
          disabled={loading}
          className="w-full max-w-xs justify-center py-3 text-base font-bold shadow-lg"
        >
          {loading ? 'Recording...' : isClockedIn ? 'Clock Out Shift' : '1-Tap Clock In'}
        </NexusButton>
      </div>
    </div>
  );
};
