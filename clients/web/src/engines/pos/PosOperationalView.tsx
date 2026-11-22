import React, { useEffect, useState, useSyncExternalStore } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusOperationalCanvasShell,
} from '@nexus/ui';
import { SplitTenderModal } from './components/SplitTenderModal';
import { SupervisorPinModal } from './components/SupervisorPinModal';
import type { PosCounterController } from './controllers/PosCounterController';
import type { SplitTenderEntry } from './types';

export interface PosOperationalViewProps {
  readonly controller: PosCounterController;
  readonly branchName: string;
  readonly cashierName: string;
  readonly workstationId: string;
  readonly onCheckoutTenders: (tenders: readonly SplitTenderEntry[]) => Promise<void>;
}

export const PosOperationalView: React.FC<PosOperationalViewProps> = ({
  controller,
  branchName,
  cashierName,
  workstationId,
  onCheckoutTenders,
}) => {
  const [isTenderOpen, setIsTenderOpen] = useState(false);
  const [isPinOpen, setIsPinOpen] = useState(false);
  const [pendingVoidId, setPendingVoidId] = useState<string | null>(null);

  // Subscribe to controller changes via useSyncExternalStore with SSR fallback
  useSyncExternalStore(
    (cb) => controller.subscribe(cb),
    () => controller.currentItems,
    () => []
  );

  const summary = controller.summary;
  const items = controller.currentItems;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F4') {
        e.preventDefault();
        setIsTenderOpen(true);
      } else if (e.key === 'F3') {
        e.preventDefault();
        controller.holdTab(`Tab ${new Date().toLocaleTimeString()}`);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [controller]);

  const handleRequestVoid = (id: string) => {
    setPendingVoidId(id);
    setIsPinOpen(true);
  };

  const handleAuthorizeVoid = (pin: string) => {
    if (pendingVoidId) {
      controller.voidItem(pendingVoidId, pin);
      setPendingVoidId(null);
    }
    setIsPinOpen(false);
  };

  return (
    <NexusOperationalCanvasShell
      stationTitle={`${branchName} • ${workstationId}`}
      cashierName={cashierName}
      statusBarRight={
        <div className="flex items-center gap-2">
          <NexusBadge variant="success">ONLINE</NexusBadge>
          <NexusBadge variant="neutral">OUTBOX: 0</NexusBadge>
        </div>
      }
    >
      <div className="grid h-full grid-cols-12 gap-4 p-4">
        {/* Left/Center Pane: Catalog Selection Grid */}
        <div className="col-span-8 flex flex-col rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-4">
          <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-3">
            <h2 className="text-base font-bold text-[var(--nx-text-primary)]">Quick Order Menu</h2>
            <div className="text-xs text-[var(--nx-text-secondary)]">Hotkeys: F3 (Hold) • F4 (Pay)</div>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-3 overflow-y-auto">
            {[
              { sku: 'BEV-001', name: 'Signature Flat White', price: '4.50' },
              { sku: 'BEV-002', name: 'Cold Brew Oat Cream', price: '5.25' },
              { sku: 'BEV-003', name: 'Iced Matcha Latte', price: '5.50' },
              { sku: 'BAK-001', name: 'Almond Butter Croissant', price: '3.75' },
              { sku: 'BAK-002', name: 'Avocado Sourdough Toast', price: '8.50' },
              { sku: 'SNK-001', name: 'Salted Caramel Cookie', price: '2.50' },
            ].map((prod) => (
              <button
                key={prod.sku}
                type="button"
                onClick={() => controller.addItem({ skuCode: prod.sku, name: prod.name, unitPrice: prod.price, quantity: 1, selectedModifiers: [] })}
                className="flex min-h-[5.5rem] flex-col justify-between rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] p-3 text-left hover:border-[var(--nx-border-focus)] active:scale-95 transition-all"
              >
                <span className="font-semibold text-sm text-[var(--nx-text-primary)]">{prod.name}</span>
                <span className="font-mono text-sm font-bold text-[var(--nx-text-primary)]">$ {prod.price}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Right Pane: Active Cart Summary */}
        <div className="col-span-4 flex flex-col rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-4">
          <div className="flex items-center justify-between border-b border-[var(--nx-border-subtle)] pb-3">
            <h3 className="text-sm font-bold text-[var(--nx-text-primary)]">Current Folio Cart ({summary.itemCount})</h3>
            <button onClick={() => controller.clearCart()} type="button" className="text-xs text-[var(--nx-text-muted)] hover:text-[var(--nx-status-danger)]">Clear</button>
          </div>

          <div className="my-3 flex-1 overflow-y-auto space-y-2 pr-1">
            {items.map((it) => (
              <div key={it.id} className="flex items-center justify-between rounded-lg bg-[var(--nx-surface-subtle)] p-2.5 text-xs">
                <div className="flex-1">
                  <div className="font-semibold text-[var(--nx-text-primary)]">{it.name}</div>
                  <div className="font-mono text-[var(--nx-text-secondary)]">{it.quantity}x @ ${it.unitPrice}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-[var(--nx-text-primary)]">${(parseFloat(it.unitPrice) * it.quantity).toFixed(2)}</span>
                  <button onClick={() => handleRequestVoid(it.id)} type="button" className="text-[var(--nx-text-muted)] hover:text-[var(--nx-status-danger)]">✕</button>
                </div>
              </div>
            ))}
          </div>

          {/* Subtotal & Totals in Tabular Nums */}
          <div className="border-t border-[var(--nx-border-subtle)] pt-3 text-xs space-y-1">
            <div className="flex justify-between text-[var(--nx-text-secondary)]">
              <span>Subtotal:</span>
              <span className="font-mono">$ {summary.subtotal}</span>
            </div>
            <div className="flex justify-between text-[var(--nx-text-secondary)]">
              <span>Tax (10%):</span>
              <span className="font-mono">$ {summary.tax}</span>
            </div>
            <div className="flex justify-between text-base font-bold text-[var(--nx-text-primary)] pt-1 border-t border-[var(--nx-border-subtle)]">
              <span>Payable Total:</span>
              <span className="font-mono">$ {summary.total}</span>
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <NexusButton variant="secondary" onClick={() => controller.holdTab(`Hold #${Date.now().toString().slice(-4)}`)} disabled={items.length === 0} className="flex-1 justify-center">Hold Tab</NexusButton>
            <NexusButton variant="primary" onClick={() => setIsTenderOpen(true)} disabled={items.length === 0} className="flex-1 justify-center">Pay (F4)</NexusButton>
          </div>
        </div>
      </div>

      <SplitTenderModal isOpen={isTenderOpen} totalDue={summary.total} currency="$" onClose={() => setIsTenderOpen(false)} onCompletePayment={async (tenders) => { setIsTenderOpen(false); await onCheckoutTenders(tenders); controller.clearCart(); }} />
      <SupervisorPinModal isOpen={isPinOpen} actionTitle="Supervisor PIN required to void item" onClose={() => setIsPinOpen(false)} onAuthorize={handleAuthorizeVoid} />
    </NexusOperationalCanvasShell>
  );
};
