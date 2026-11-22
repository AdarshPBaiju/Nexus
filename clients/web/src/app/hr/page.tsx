'use client';

import React, { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { StaffDirectoryView } from '../../engines/hr/StaffDirectoryView';
import { EssPunchClockWidget } from '../../engines/hr/EssPunchClockWidget';
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
      employeeId: 'EMP-01',
      punchType,
      timestamp: new Date().toISOString(),
      verificationMethod: 'GPS_GEOFENCE',
      locationFenced: true,
    };
    setPunches((prev) => [newRecord, ...prev]);
  };

  return (
    <>
      <Navbar />
      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
          <div>
            <StaffDirectoryView
              employees={employees}
              onSelectEmployee={setSelectedEmpId}
              onRegisterEmployee={() => {}}
            />
            {selectedEmpId && (
              <div
                style={{
                  marginTop: '16px',
                  padding: '12px 16px',
                  backgroundColor: 'var(--nx-surface-card)',
                  borderRadius: '8px',
                  border: '1px solid var(--nx-border-default)',
                  fontSize: '13px',
                }}
              >
                Selected Employee: <strong>{selectedEmpId}</strong>
              </div>
            )}
          </div>
          <div>
            <EssPunchClockWidget
              employeeName="Sarah Jenkins (NX-001)"
              department="BARISTA"
              recentPunches={punches}
              onRecordPunch={handlePunch}
            />
          </div>
        </div>
      </main>
    </>
  );
}
