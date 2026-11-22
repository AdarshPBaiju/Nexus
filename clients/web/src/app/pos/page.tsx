'use client';

import React, { useMemo, useState } from 'react';
import { PosOperationalView } from '../../engines/pos/PosOperationalView';
import { PosCounterController } from '../../engines/pos/controllers/PosCounterController';
import { useAuth } from '../../runtime/auth/AuthContext';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { SplitTenderEntry } from '../../engines/pos/types';

export default function PosPage(): React.JSX.Element {
  const { session } = useAuth();

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
      name: 'Flat White',
      unitPrice: '4.20',
      quantity: 2,
      selectedModifiers: [{ id: 'MOD-OAT', name: 'Oat Milk', priceDelta: '0.60' }],
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
    const summary = tenders.map((t) => `${t.tenderType} $${t.amount}`).join(' · ');
    setLastPayment(`Order settled for $${controller.summary.total} (${summary})`);
    controller.clearCart();
  };

  return (
    <NexusBox
      style={{
        flex: 1,
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {lastPayment && (
        <NexusBox
          padding="8px 16px"
          style={{
            flexShrink: 0,
            backgroundColor: 'var(--nx-status-success-subtle)',
            borderBottom: '1px solid var(--nx-border-default)',
          }}
        >
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
              <NexusBadge variant="success" dot label="Settled" />
              <NexusText variant="label">{lastPayment}</NexusText>
            </NexusStack>
            <NexusButton variant="ghost" size="sm" onClick={() => setLastPayment(null)}>
              <NexusText variant="caption">Dismiss</NexusText>
            </NexusButton>
          </NexusStack>
        </NexusBox>
      )}

      <NexusBox style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
        <PosOperationalView
          controller={controller}
          branchName={session.branchName}
          cashierName={session.name}
          workstationId={session.workstationId}
          onCheckoutTenders={handleCheckout}
        />
      </NexusBox>
    </NexusBox>
  );
}
