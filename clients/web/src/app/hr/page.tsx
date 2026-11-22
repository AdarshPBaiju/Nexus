'use client';

import React, { useState } from 'react';
import { StaffDirectoryView } from '../../engines/hr/StaffDirectoryView';
import { EssPunchClockWidget } from '../../engines/hr/EssPunchClockWidget';
import {
  NexusBadge,
  NexusBox,
  NexusCard,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { useAuth } from '../../runtime/auth/AuthContext';
import type { AttendanceRecordDto, EmployeeDto } from '../../engines/hr/types';

const INITIAL_STAFF: EmployeeDto[] = [
  {
    id: 'EMP-01',
    employeeCode: 'NX-001',
    firstName: 'Sarah',
    lastName: 'Jenkins',
    email: 'sarah.j@artisan.nexus',
    department: 'BARISTA',
    designation: 'Head Barista',
    employmentType: 'FULL_TIME',
    status: 'ACTIVE',
    isActive: true,
    isOnDuty: true,
    lastPunchAt: '2026-11-22T08:00:00Z',
  },
  {
    id: 'EMP-02',
    employeeCode: 'NX-002',
    firstName: 'Marcus',
    lastName: 'Vance',
    email: 'marcus.v@artisan.nexus',
    department: 'KITCHEN',
    designation: 'Sous Chef',
    employmentType: 'FULL_TIME',
    status: 'ACTIVE',
    isActive: true,
    isOnDuty: true,
    lastPunchAt: '2026-11-22T07:45:00Z',
  },
  {
    id: 'EMP-03',
    employeeCode: 'NX-003',
    firstName: 'Chloe',
    lastName: 'Bennett',
    email: 'chloe.b@artisan.nexus',
    department: 'BARISTA',
    designation: 'Senior Barista',
    employmentType: 'PART_TIME',
    status: 'ACTIVE',
    isActive: true,
    isOnDuty: false,
    lastPunchAt: '2026-11-21T16:00:00Z',
  },
  {
    id: 'EMP-04',
    employeeCode: 'NX-004',
    firstName: 'David',
    lastName: 'Chen',
    email: 'david.c@artisan.nexus',
    department: 'MANAGEMENT',
    designation: 'General Manager',
    employmentType: 'FULL_TIME',
    status: 'ACTIVE',
    isActive: true,
    isOnDuty: true,
    lastPunchAt: '2026-11-22T07:30:00Z',
  },
];

export default function HrPage(): React.JSX.Element {
  const { session } = useAuth();
  const [employees] = useState<EmployeeDto[]>(INITIAL_STAFF);
  const [punches, setPunches] = useState<AttendanceRecordDto[]>([
    {
      id: 'ATT-01',
      employeeId: 'EMP-01',
      branchId: session.branchId,
      businessDate: '2026-11-22',
      clockInUtc: '2026-11-22T08:00:00Z',
      clockOutUtc: null,
      clockInMethod: 'BIOMETRIC',
      isManualOverride: false,
    },
  ]);
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);

  const activePunch = punches.find(
    (punch) => punch.employeeId === session.id && !punch.clockOutUtc
  );

  const handleClockIn = async () => {
    const now = new Date();
    setPunches((prev) => [
      {
        id: `ATT-${now.getTime()}`,
        employeeId: session.id,
        branchId: session.branchId,
        businessDate: now.toISOString().split('T')[0],
        clockInUtc: now.toISOString(),
        clockOutUtc: null,
        clockInMethod: 'WEB',
        isManualOverride: false,
      },
      ...prev,
    ]);
  };

  const handleClockOut = async () => {
    const now = new Date().toISOString();
    setPunches((prev) =>
      prev.map((punch) =>
        punch.employeeId === session.id && !punch.clockOutUtc
          ? { ...punch, clockOutUtc: now }
          : punch
      )
    );
  };

  return (
    <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <NexusStack direction="row" gap="var(--nx-space-6)" align="start" style={{ flexWrap: 'wrap' }}>
        <NexusBox style={{ flex: '1 1 360px', minWidth: 0 }}>
          <StaffDirectoryView
            employees={employees}
            onSelectEmployee={setSelectedEmpId}
            onRegisterEmployee={() => {}}
          />
          {selectedEmpId && (
            <NexusCard elevation="subtle" style={{ marginTop: 'var(--nx-space-4)', padding: 'var(--nx-space-3)' }}>
              <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
                <NexusBadge variant="info" label="Roster Profile" />
                <NexusText variant="label">Employee ID: {selectedEmpId}</NexusText>
              </NexusStack>
            </NexusCard>
          )}
        </NexusBox>

        <NexusBox style={{ flex: '1 1 320px', minWidth: 0 }}>
          <EssPunchClockWidget
            employeeId={session.id}
            branchId={session.branchId}
            activePunch={activePunch ?? null}
            onClockIn={handleClockIn}
            onClockOut={handleClockOut}
          />
        </NexusBox>
      </NexusStack>
    </NexusStack>
  );
}
