'use client';

import React, { useEffect, useMemo, useState, useSyncExternalStore } from 'react';
import { NexusBadge, NexusOperationalCanvasShell, NexusSearchInput } from '@nexus/ui';
import { SplitTenderModal } from './components/SplitTenderModal';
import { SupervisorPinModal } from './components/SupervisorPinModal';
import { ModifierSelectionModal } from './components/ModifierSelectionModal';
import { PosCartRail } from './components/PosCartRail';
import { PosProductGrid } from './components/PosProductGrid';
import { CAFE_CATEGORIES, CAFE_PRODUCTS, type RichMenuItem } from './cafeCatalogData';
import type { PosCounterController } from './controllers/PosCounterController';
import type { SplitTenderEntry } from './types';
import type { ModifierOptionDto } from './catalog.types';

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
  const [selectedCat, setSelectedCat] = useState<string>('cat-all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isTenderOpen, setIsTenderOpen] = useState(false);
  const [isPinOpen, setIsPinOpen] = useState(false);
  const [pendingVoidId, setPendingVoidId] = useState<string | null>(null);
  const [customizingItem, setCustomizingItem] = useState<RichMenuItem | null>(null);

  useSyncExternalStore(
    (cb) => controller.subscribe(cb),
    () => controller.currentItems,
    () => controller.currentItems
  );

  const summary = controller.summary;
  const items = controller.currentItems;
  const heldTabs = controller.allHeldTabs;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F4') {
        e.preventDefault();
        setIsTenderOpen(true);
      } else if (e.key === 'F3') {
        e.preventDefault();
        controller.holdTab(`Held ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [controller]);

  const filteredProducts = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return CAFE_PRODUCTS.filter((prod) => {
      const matchCat =
        selectedCat === 'cat-all'
          ? true
          : selectedCat === 'cat-pop'
          ? Boolean(prod.isPopular)
          : prod.categoryId === selectedCat;
      const matchSearch =
        !query ||
        prod.name.toLowerCase().includes(query) ||
        prod.skuCode.toLowerCase().includes(query);
      return matchCat && matchSearch;
    });
  }, [selectedCat, searchQuery]);

  const handleAddItem = (prod: RichMenuItem, selectedMods: readonly ModifierOptionDto[] = []) => {
    controller.addItem({
      skuCode: prod.skuCode,
      name: prod.name,
      unitPrice: prod.basePrice,
      quantity: 1,
      selectedModifiers: selectedMods.map((mod) => ({
        id: mod.id,
        name: mod.name,
        priceDelta: mod.priceDelta,
      })),
    });
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
      stationTitle={`${branchName} · ${workstationId}`}
      cashierName={cashierName}
      statusBarRight={
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <NexusBadge variant="success" dot label="Online" />
          <NexusBadge variant="neutral" label="Outbox 0" />
          <NexusBadge variant="info" label="Shift open" />
        </div>
      }
    >
      <div className="nx-pos-workspace">
        <section className="nx-pos-panel" aria-label="Product catalog">
          <div
            style={{
              flexShrink: 0,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 12px',
              borderBottom: '1px solid var(--nx-border-subtle)',
              overflowX: 'auto',
            }}
          >
            {CAFE_CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                type="button"
                onClick={() => setSelectedCat(cat.id)}
                aria-pressed={selectedCat === cat.id}
                className={`nx-chip nx-focusable ${selectedCat === cat.id ? 'nx-chip--active' : ''}`.trim()}
              >
                {cat.name}
              </button>
            ))}

            <div style={{ marginInlineStart: 'auto', minWidth: '160px' }}>
              <NexusSearchInput
                value={searchQuery}
                onChange={setSearchQuery}
                placeholderKey="Search SKU..."
              />
            </div>
          </div>

          <div className="nx-scroll-area" style={{ flex: 1, minHeight: 0, padding: '10px 12px 12px' }}>
            <PosProductGrid
              products={filteredProducts}
              onAdd={handleAddItem}
              onCustomize={(prod) => setCustomizingItem(prod)}
            />
          </div>
        </section>

        <PosCartRail
          items={items}
          summary={summary}
          heldTabs={heldTabs}
          onClear={() => controller.clearCart()}
          onUpdateQuantity={(id, delta) => controller.updateQuantity(id, delta)}
          onRequestVoid={(id) => {
            setPendingVoidId(id);
            setIsPinOpen(true);
          }}
          onApplyDiscount={(d) => controller.applyDiscount(d)}
          onHoldTab={() => controller.holdTab(`Held ${heldTabs.length + 1}`)}
          onOpenPay={() => setIsTenderOpen(true)}
        />
      </div>

      <SplitTenderModal
        isOpen={isTenderOpen}
        totalDue={summary.total}
        currency="$"
        onClose={() => setIsTenderOpen(false)}
        onCompletePayment={onCheckoutTenders}
      />
      <SupervisorPinModal
        isOpen={isPinOpen}
        actionTitle="Manager PIN required to void this cart line"
        onClose={() => setIsPinOpen(false)}
        onAuthorize={handleAuthorizeVoid}
      />
      {customizingItem && (
        <ModifierSelectionModal
          isOpen={true}
          item={customizingItem}
          onConfirm={(mods) => {
            handleAddItem(customizingItem, mods);
            setCustomizingItem(null);
          }}
          onCancel={() => setCustomizingItem(null)}
        />
      )}
    </NexusOperationalCanvasShell>
  );
};
