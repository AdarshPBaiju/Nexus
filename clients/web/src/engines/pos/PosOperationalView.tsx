'use client';

import React, { useEffect, useState, useSyncExternalStore, useMemo } from 'react';
import { NexusBadge, NexusOperationalCanvasShell } from '@nexus/ui';
import { SplitTenderModal } from './components/SplitTenderModal';
import { SupervisorPinModal } from './components/SupervisorPinModal';
import { ModifierSelectionModal } from './components/ModifierSelectionModal';
import { PosCartRail } from './components/PosCartRail';
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
        controller.holdTab(`Tab ${new Date().toLocaleTimeString()}`);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [controller]);

  const filteredProducts = useMemo(() => {
    return CAFE_PRODUCTS.filter((prod) => {
      const matchCat =
        selectedCat === 'cat-all'
          ? true
          : selectedCat === 'cat-pop'
          ? !!prod.isPopular
          : prod.categoryId === selectedCat;
      const matchSearch =
        !searchQuery ||
        prod.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        prod.skuCode.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchSearch;
    });
  }, [selectedCat, searchQuery]);

  const handleAddItem = (prod: RichMenuItem, selectedMods: readonly ModifierOptionDto[] = []) => {
    controller.addItem({
      skuCode: prod.skuCode,
      name: prod.name,
      unitPrice: prod.basePrice,
      quantity: 1,
      selectedModifiers: selectedMods.map((m) => ({
        groupName: 'Customization',
        optionName: m.name,
        priceDelta: m.priceDelta,
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
      stationTitle={`${branchName} • ${workstationId}`}
      cashierName={cashierName}
      statusBarRight={
        <div className="flex items-center gap-2">
          <NexusBadge variant="success">ONLINE</NexusBadge>
          <NexusBadge variant="neutral">OUTBOX: 0</NexusBadge>
        </div>
      }
    >
      <div className="grid h-full grid-cols-12 gap-3 p-3 overflow-hidden">
        {/* Left / Center Catalog Rail */}
        <div className="col-span-8 flex flex-col rounded-2xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] p-3 overflow-hidden">
          {/* Category Tabs & Quick Search */}
          <div className="flex items-center gap-2 pb-2.5 border-b border-[var(--nx-border-subtle)] overflow-x-auto">
            {CAFE_CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                type="button"
                onClick={() => setSelectedCat(cat.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedCat === cat.id
                    ? 'bg-primary text-on-primary shadow-sm'
                    : 'bg-surface-container text-outline hover:text-on-surface'
                }`}
              >
                {cat.name}
              </button>
            ))}
            <input
              type="text"
              placeholder="Search / Scan SKU..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="ml-auto w-36 h-7 px-2 text-xs rounded-lg bg-surface-container border border-outline-variant text-on-surface outline-none focus:border-primary"
            />
          </div>

          {/* Product Grid */}
          <div className="mt-3 flex-1 grid grid-cols-3 gap-2.5 overflow-y-auto pr-1">
            {filteredProducts.map((prod) => (
              <div
                key={prod.id}
                className="flex flex-col justify-between rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] p-3 hover:border-primary transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="text-[10px] font-mono text-outline uppercase">{prod.preparationStation}</span>
                    {prod.badge && <NexusBadge variant="neutral" label={prod.badge} />}
                  </div>
                  <h3 className="font-semibold text-xs text-[var(--nx-text-primary)] leading-tight">{prod.name}</h3>
                  <p className="text-[11px] text-outline line-clamp-1 mt-0.5">{prod.description}</p>
                </div>
                <div className="flex items-center justify-between pt-2 mt-2 border-t border-[var(--nx-border-subtle)]">
                  <span className="font-mono text-xs font-bold text-primary">$ {prod.basePrice}</span>
                  <div className="flex gap-1">
                    {prod.modifierGroups && prod.modifierGroups.length > 0 && (
                      <button
                        type="button"
                        onClick={() => setCustomizingItem(prod)}
                        className="px-2 py-1 rounded bg-surface-container hover:bg-surface-container-high text-[10px] font-semibold text-outline"
                      >
                        Custom
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleAddItem(prod)}
                      className="px-2.5 py-1 rounded bg-primary text-on-primary text-[10px] font-bold shadow-sm active:scale-95 transition-all"
                    >
                      + Add
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Active Cart Rail */}
        <PosCartRail
          items={items}
          summary={summary}
          heldTabs={heldTabs}
          onClear={() => controller.clearCart()}
          onUpdateQuantity={(id, delta) => controller.updateQuantity(id, delta)}
          onRequestVoid={(id) => { setPendingVoidId(id); setIsPinOpen(true); }}
          onApplyDiscount={(d) => controller.applyDiscount(d)}
          onHoldTab={() => controller.holdTab(`Tab ${heldTabs.length + 1}`)}
          onOpenPay={() => setIsTenderOpen(true)}
        />
      </div>

      <SplitTenderModal isOpen={isTenderOpen} totalDue={summary.total} currency="$" onClose={() => setIsTenderOpen(false)} onCompletePayment={async (tenders) => { await onCheckoutTenders(tenders); }} />
      <SupervisorPinModal isOpen={isPinOpen} actionTitle="Manager PIN (9999) required to void cart line" onClose={() => setIsPinOpen(false)} onAuthorize={handleAuthorizeVoid} />
      {customizingItem && (
        <ModifierSelectionModal
          isOpen={true}
          item={customizingItem}
          onConfirm={(mods) => { handleAddItem(customizingItem, mods); setCustomizingItem(null); }}
          onCancel={() => setCustomizingItem(null)}
        />
      )}
    </NexusOperationalCanvasShell>
  );
};
