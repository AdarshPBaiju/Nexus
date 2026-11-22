'use client';

import React, { useState } from 'react';
import { ShiftRegisterConsole } from '../../engines/finance/ShiftRegisterConsole';
import {
  NexusBadge,
  NexusBox,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { useAuth } from '../../runtime/auth/AuthContext';
import type { ShiftRegisterSessionDto } from '../../engines/finance/types';

export default function FinancePage(): React.JSX.Element {
  const { session: authSession } = useAuth();

  const [session, setSession] = useState<ShiftRegisterSessionDto>({
    id: 'SES-2026-0089',
    workstationId: authSession.workstationId,
    cashierUserId: authSession.id,
    treasuryAccountId: 'TRS-CASH-DRAWER-01',
    status: 'OPEN',
    openedAt: new Date(Date.now() - 14400000).toISOString(),
    openingFloat: '200.00',
    systemCashTotal: '542.50',
    expectedCashTotal: '742.50',
    actualCashCount: null,
    varianceAmount: null,
  });

  const [statusMsg, setStatusMsg] = useState<string | null>(null);


  const handleOpen = async (float: string) => {
    setSession((s) => ({ ...s, openingFloat: float, status: 'OPEN' }));
    setStatusMsg(`Shift opened with float: $${float}`);
  };

  const handleClose = async (actualCount: string) => {
    const diff = (parseFloat(actualCount) - parseFloat(session.expectedCashTotal)).toFixed(2);
    setSession((s) => ({
      ...s,
      status: 'CLOSED',
      closedAt: new Date().toISOString(),
      actualCashCount: actualCount,
      varianceAmount: diff,
    }));
    setStatusMsg(`Shift closed. Actual: $${actualCount} | Variance: $${diff}`);
  };

  const handleExpense = async (amount: string, reason: string) => {
    setSession((s) => ({
      ...s,
      expectedCashTotal: (parseFloat(s.expectedCashTotal) - parseFloat(amount)).toFixed(2),
    }));
    setStatusMsg(`Recorded petty cash: $${amount} for ${reason}`);
  };

  return (
    <NexusStack gap="var(--nx-space-4)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {statusMsg && (
        <NexusBox
          padding="var(--nx-space-2) var(--nx-space-4)"
          style={{
            backgroundColor: 'var(--nx-surface-card)',
            borderRadius: '6px',
            border: '1px solid var(--nx-border-default)',
          }}
        >
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <NexusBadge variant="info" label="Audit Event" />
            <NexusText variant="label">{statusMsg}</NexusText>
          </NexusStack>
        </NexusBox>
      )}

      <ShiftRegisterConsole
        initialSession={session}
        onOpenShift={handleOpen}
        onCloseShift={handleClose}
        onAddExpense={handleExpense}
      />
    </NexusStack>
  );
}
