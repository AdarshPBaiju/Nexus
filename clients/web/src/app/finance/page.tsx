'use client';

import React, { useState } from 'react';
import { Navbar } from '../components/Navbar';
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
    sessionId: 'SES-2026-0089',
    cashierId: authSession.id,
    cashierName: authSession.name,
    workstationId: authSession.workstationId,
    status: 'OPEN',
    openedAt: new Date(Date.now() - 14400000).toISOString(),
    openingFloat: '200.00',
    expectedCash: '742.50',
    cashSales: '542.50',
    paidOutTotal: '0.00',
    currency: 'USD',
    expenses: [],
  });

  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleOpen = async (float: string) => {
    setSession((s) => ({ ...s, openingFloat: float, status: 'OPEN' }));
    setStatusMsg(`Shift opened with float: $${float}`);
  };

  const handleClose = async (actualCount: string) => {
    const diff = (parseFloat(actualCount) - parseFloat(session.expectedCash)).toFixed(2);
    setSession((s) => ({
      ...s,
      status: 'CLOSED',
      closingCashActual: actualCount,
      varianceAmount: diff,
    }));
    setStatusMsg(`Shift closed. Actual: $${actualCount} | Variance: $${diff}`);
  };

  const handleExpense = async (amount: string, reason: string) => {
    setSession((s) => ({
      ...s,
      paidOutTotal: (parseFloat(s.paidOutTotal) + parseFloat(amount)).toFixed(2),
      expectedCash: (parseFloat(s.expectedCash) - parseFloat(amount)).toFixed(2),
      expenses: [...s.expenses, { id: `EXP-${Date.now()}`, amount, reason, timestamp: new Date().toISOString() }],
    }));
    setStatusMsg(`Recorded expense: $${amount} for ${reason}`);
  };

  return (
    <NexusBox>
      <Navbar />

      {statusMsg && (
        <NexusBox
          padding="var(--nx-space-2) var(--nx-space-6)"
          style={{
            backgroundColor: 'var(--nx-surface-card)',
            borderBottom: '1px solid var(--nx-border-default)',
          }}
        >
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <NexusBadge variant="info" label="Audit Event" />
            <NexusText variant="label">{statusMsg}</NexusText>
          </NexusStack>
        </NexusBox>
      )}

      <NexusBox
        padding="var(--nx-space-6)"
        style={{ maxWidth: '1200px', margin: '0 auto', width: '100%' }}
      >
        <ShiftRegisterConsole
          initialSession={session}
          onOpenShift={handleOpen}
          onCloseShift={handleClose}
          onAddExpense={handleExpense}
        />
      </NexusBox>
    </NexusBox>
  );
}
