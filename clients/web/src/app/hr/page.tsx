'use client';

import React, { useState } from 'react';
import { NexusMainTopNavbar } from '../components/NexusMainTopNavbar';
import { NexusEnterpriseSidebar } from '../components/NexusEnterpriseSidebar';
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
import type { EmployeeDto, PunchRecordDto } from '../../engines/hr/types';

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
    isOnDuty: true,
    lastPunchAt: '2026-11-22T07:30:00Z',
  },
];

export default function HrPage(): React.JSX.Element {
  const { session } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [employees] = useState<EmployeeDto[]>(INITIAL_STAFF);
  const [punches, setPunches] = useState<PunchRecordDto[]>([
    {
      id: 'PCH-01',
      employeeId: 'EMP-01',
      punchType: 'CLOCK_IN',
      timestamp: '2026-11-22T08:00:00Z',
      verificationMethod: 'FINGERPRINT_BIOMETRIC',
      locationFenced: true,
    },
  ]);
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);

  const handlePunch = async (punchType: 'CLOCK_IN' | 'CLOCK_OUT') => {
    const newRecord: PunchRecordDto = {
      id: `PCH-${Date.now()}`,
      employeeId: session.id,
      punchType,
      timestamp: new Date().toISOString(),
      verificationMethod: 'GPS_GEOFENCE',
      locationFenced: true,
    };
    setPunches((prev) => [newRecord, ...prev]);
  };

  return (
    <NexusBox style={{ minHeight: '100vh', backgroundColor: 'var(--nx-surface-bg)' }}>
      <NexusMainTopNavbar
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <NexusEnterpriseSidebar isOpen={isSidebarOpen} />

      <NexusBox
        style={{
          marginLeft: isSidebarOpen ? '280px' : 0,
          marginTop: '56px',
          padding: 'var(--nx-space-8) var(--nx-space-6)',
          transition: 'margin-left 0.2s ease',
        }}
      >
        <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <NexusStack direction="row" gap="var(--nx-space-6)" align="start">
            <NexusBox style={{ flex: 2 }}>
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

            <NexusBox style={{ flex: 1 }}>
              <EssPunchClockWidget
                employeeName={`${session.name} (${session.id})`}
                department="BARISTA"
                recentPunches={punches}
                onRecordPunch={handlePunch}
              />
            </NexusBox>
          </NexusStack>
        </NexusStack>
      </NexusBox>
    </NexusBox>
  );
}
