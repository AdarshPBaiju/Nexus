'use client';

import React, { useMemo, useState } from 'react';
import { NexusMainTopNavbar } from '../components/NexusMainTopNavbar';
import { NexusEnterpriseSidebar } from '../components/NexusEnterpriseSidebar';
import { PosOperationalView } from '../../engines/pos/PosOperationalView';
import { PosCounterController } from '../../engines/pos/controllers/PosCounterController';
import { useAuth } from '../../runtime/auth/AuthContext';
import {
  NexusBadge,
  NexusBox,
  NexusButton,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import type { SplitTenderEntry } from '../../engines/pos/types';

export default function PosPage(): React.JSX.Element {
  const { session } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const controller = useMemo(() => {
    const c = PosCounterController.create();
    c.addItem({
      skuCode: 'ESP-01',
      name: 'Espresso Double Shot',
      unitPrice: '3.50',
      quantity: 1,
      selectedModifiers: [],
    });
    c.addItem({
      skuCode: 'FW-02',
      name: 'Flat White (Oat Milk)',
      unitPrice: '4.80',
      quantity: 2,
      selectedModifiers: [{ groupName: 'Milk', optionName: 'Oat Milk', priceDelta: '0.60' }],
    });
    c.addItem({
      skuCode: 'CRS-03',
      name: 'Almond Butter Croissant',
      unitPrice: '4.20',
      quantity: 1,
      selectedModifiers: [],
    });
    return c;
  }, []);

  const [lastPayment, setLastPayment] = useState<string | null>(null);

  const handleCheckout = async (tenders: readonly SplitTenderEntry[]) => {
    const summary = tenders.map((t) => `${t.tenderType}: $${t.amount}`).join(', ');
    setLastPayment(`Settled $${controller.summary.total} via [${summary}]`);
    controller.clearCart();
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
          height: 'calc(100vh - 56px)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'margin-left 0.2s ease',
        }}
      >
        {lastPayment && (
          <NexusBox
            padding="var(--nx-space-2) var(--nx-space-6)"
            style={{
              backgroundColor: 'var(--nx-status-success-subtle)',
              borderBottom: '1px solid var(--nx-border-default)',
            }}
          >
            <NexusStack direction="row" align="center" justify="space-between">
              <NexusText variant="label">✓ {lastPayment}</NexusText>
              <NexusButton variant="ghost" size="sm" onClick={() => setLastPayment(null)}>
                <NexusText variant="caption">✕ Dismiss</NexusText>
              </NexusButton>
            </NexusStack>
          </NexusBox>
        )}

        <NexusBox style={{ flex: 1, overflow: 'hidden' }}>
          <PosOperationalView
            controller={controller}
            branchName={session.branchName}
            cashierName={session.name}
            workstationId={session.workstationId}
            onCheckoutTenders={handleCheckout}
          />
        </NexusBox>
      </NexusBox>
    </NexusBox>
  );
}
