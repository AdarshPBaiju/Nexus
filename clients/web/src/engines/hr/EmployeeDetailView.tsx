import React from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusDetailPageShell,
} from '@nexus/ui';
import type { AttendanceRecordDto, ContractDto, EmployeeDto } from './types';

export interface EmployeeDetailViewProps {
  readonly employee: EmployeeDto;
  readonly contract?: ContractDto | null;
  readonly attendance: readonly AttendanceRecordDto[];
  readonly onBack: () => void;
  readonly onClockAction: () => void;
}

export const EmployeeDetailView: React.FC<EmployeeDetailViewProps> = ({
  employee,
  contract,
  attendance,
  onBack,
  onClockAction,
}) => {
  return (
    <NexusDetailPageShell
      title={`${employee.firstName} ${employee.lastName}`}
      subtitle={`${employee.employeeCode} • ${employee.department} • ${employee.designation}`}
      headerActions={
        <div className="flex items-center gap-3">
          <NexusButton variant="secondary" onClick={onBack}>
            ← Back to Directory
          </NexusButton>
          <NexusButton variant="primary" onClick={onClockAction}>
            Punch Clock
          </NexusButton>
        </div>
      }
    >
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Employment Contract Card */}
        <div className="rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
          <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-3">
            <h3 className="text-sm font-bold text-[var(--nx-text-primary)]">Employment Contract</h3>
            {contract?.isCurrent && <NexusBadge variant="success">Active Terms</NexusBadge>}
          </div>

          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[var(--nx-text-secondary)]">Contract Type:</span>
              <span className="font-medium text-[var(--nx-text-primary)]">{contract?.contractType ?? 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--nx-text-secondary)]">Compensation (Confidential):</span>
              <span className="font-mono font-bold text-[var(--nx-text-primary)]">
                {contract ? `${contract.currency} ••••••` : 'Unassigned'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--nx-text-secondary)]">Effective Date:</span>
              <span className="text-[var(--nx-text-primary)]">{contract?.validFrom ?? 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Status Card */}
        <div className="rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
          <div className="border-b border-[var(--nx-border-subtle)] pb-3">
            <h3 className="text-sm font-bold text-[var(--nx-text-primary)]">Workforce Status</h3>
          </div>
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[var(--nx-text-secondary)]">Directory Status:</span>
              <NexusBadge variant={employee.isActive ? 'success' : 'neutral'}>
                {employee.isActive ? 'Active Employee' : 'Archived'}
              </NexusBadge>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--nx-text-secondary)]">Logged Shifts (30d):</span>
              <span className="font-mono font-medium text-[var(--nx-text-primary)]">{attendance.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Attendance History */}
      <div className="mt-8 rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-5">
        <h3 className="text-sm font-bold text-[var(--nx-text-primary)] mb-4">Recent Attendance Punches</h3>
        <div className="overflow-x-auto">
          <table className="nx-data-table">
            <thead className="border-b border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]">
              <tr>
                <th className="px-3 py-2">BUSINESS DATE</th>
                <th className="px-3 py-2">CLOCK-IN (UTC)</th>
                <th className="px-3 py-2">CLOCK-OUT (UTC)</th>
                <th className="px-3 py-2">METHOD</th>
                <th className="px-3 py-2">OVERRIDE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--nx-border-subtle)]">
              {attendance.map((rec) => (
                <tr key={rec.id}>
                  <td className="px-3 py-2 font-mono font-medium text-[var(--nx-text-primary)]">{rec.businessDate}</td>
                  <td className="px-3 py-2 font-mono text-[var(--nx-text-secondary)]">{rec.clockInUtc}</td>
                  <td className="px-3 py-2 font-mono text-[var(--nx-text-secondary)]">{rec.clockOutUtc ?? 'In Progress...'}</td>
                  <td className="px-3 py-2">{rec.clockInMethod}</td>
                  <td className="px-3 py-2">
                    {rec.isManualOverride ? (
                      <NexusBadge variant="warning">Manager Corrected</NexusBadge>
                    ) : (
                      <span className="text-[var(--nx-text-muted)]">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </NexusDetailPageShell>
  );
};
