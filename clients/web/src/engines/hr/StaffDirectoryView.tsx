import React, { useMemo, useState } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusListingPageShell,
  NexusSearchInput,
  NexusSelect,
  NexusText,
} from '@nexus/ui';
import type { EmployeeDto } from './types';

export interface StaffDirectoryViewProps {
  readonly employees: readonly EmployeeDto[];
  readonly onSelectEmployee: (employeeId: string) => void;
  readonly onRegisterEmployee: () => void;
}

export const StaffDirectoryView: React.FC<StaffDirectoryViewProps> = ({
  employees,
  onSelectEmployee,
  onRegisterEmployee,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');

  const departments = useMemo(() => {
    const set = new Set<string>();
    employees.forEach((e) => set.add(e.department));
    return ['ALL', ...Array.from(set)];
  }, [employees]);

  const filtered = useMemo(() => {
    return employees.filter((e) => {
      const matchSearch =
        e.employeeCode.toLowerCase().includes(searchTerm.toLowerCase()) ||
        `${e.firstName} ${e.lastName}`.toLowerCase().includes(searchTerm.toLowerCase());
      const matchDept = selectedDept === 'ALL' || e.department === selectedDept;
      return matchSearch && matchDept;
    });
  }, [employees, searchTerm, selectedDept]);

  return (
    <NexusListingPageShell
      title="Staff Directory"
      subtitle="Manage employee master records, roles, departments, and active workforce status."
      primaryAction={
        <NexusButton variant="primary" onClick={onRegisterEmployee}>
          + Register Employee
        </NexusButton>
      }
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div style={{ width: '280px' }}>
          <NexusSearchInput
            placeholderKey="Search by code or name..."
            value={searchTerm}
            onChange={setSearchTerm}
          />
        </div>

        <div className="flex items-center gap-2">
          <NexusText variant="caption" role="secondary">Department:</NexusText>
          <div style={{ width: '180px' }}>
            <NexusSelect
              value={selectedDept}
              onChange={setSelectedDept}
              options={departments.map((dept) => ({ value: dept, label: dept }))}
            />
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)]">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)] text-xs text-[var(--nx-text-secondary)]">
            <tr>
              <th className="px-4 py-3">CODE</th>
              <th className="px-4 py-3">FULL NAME</th>
              <th className="px-4 py-3">DEPARTMENT</th>
              <th className="px-4 py-3">DESIGNATION</th>
              <th className="px-4 py-3">STATUS</th>
              <th className="px-4 py-3 text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--nx-border-subtle)]">
            {filtered.map((emp) => (
              <tr
                key={emp.id}
                onClick={() => onSelectEmployee(emp.id)}
                className="cursor-pointer hover:bg-[var(--nx-surface-subtle)] transition-colors"
              >
                <td className="px-4 py-3 font-mono font-medium text-[var(--nx-text-primary)]">
                  {emp.employeeCode}
                </td>
                <td className="px-4 py-3 font-medium text-[var(--nx-text-primary)]">
                  {emp.firstName} {emp.lastName}
                </td>
                <td className="px-4 py-3 text-[var(--nx-text-secondary)]">{emp.department}</td>
                <td className="px-4 py-3 text-[var(--nx-text-secondary)]">{emp.designation}</td>
                <td className="px-4 py-3">
                  <NexusBadge variant={emp.isActive ? 'success' : 'neutral'}>
                    {emp.isActive ? 'Active' : 'Inactive'}
                  </NexusBadge>
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectEmployee(emp.id);
                    }}
                    className="text-xs font-semibold text-[var(--nx-action-primary)] hover:underline"
                  >
                    View Record →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </NexusListingPageShell>
  );
};
