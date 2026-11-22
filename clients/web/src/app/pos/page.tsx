'use client';

import React, { useMemo, useState } from 'react';
import { Navbar } from '../components/Navbar';
import { PosOperationalView } from '../../engines/pos/PosOperationalView';
import { PosCounterController } from '../../engines/pos/controllers/PosCounterController';
import type { SplitTenderEntry } from '../../engines/pos/types';

export default function PosPage(): React.JSX.Element {
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
    <>
      <Navbar />
      {lastPayment && (
        <div
          style={{
            padding: '10px 24px',
            backgroundColor: 'var(--nx-status-success-subtle)',
            color: 'var(--nx-status-success-text)',
            fontSize: '13px',
            fontWeight: 600,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>✓ {lastPayment}</span>
          <button
            onClick={() => setLastPayment(null)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}
          >
            ✕
          </button>
        </div>
      )}
      <div style={{ flex: 1, height: 'calc(100vh - 60px)' }}>
        <PosOperationalView
          controller={controller}
          branchName="Artisan Coffee Roasters — London SoHo"
          cashierName="Sarah Jenkins"
          workstationId="WS-LND-01"
          onCheckoutTenders={handleCheckout}
        />
      </div>
    </>
  );
}
