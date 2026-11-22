'use client';

import React, { useState } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusCard,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { ReceiveDeliveryModal } from './components/ReceiveDeliveryModal';

interface IngredientStock {
  id: string;
  name: string;
  category: string;
  currentStock: number;
  unit: string;
  minThreshold: number;
  costPerUnit: string;
  status: 'OPTIMAL' | 'LOW' | 'CRITICAL';
}

const INITIAL_INGREDIENTS: IngredientStock[] = [
  { id: 'ING-01', name: 'Ethiopian Yirgacheffe Beans', category: 'Coffee', currentStock: 18400, unit: 'g', minThreshold: 5000, costPerUnit: '$0.024/g', status: 'OPTIMAL' },
  { id: 'ING-02', name: 'Oatly Barista Oat Milk', category: 'Dairy/Alt', currentStock: 8200, unit: 'ml', minThreshold: 10000, costPerUnit: '$0.003/ml', status: 'LOW' },
  { id: 'ING-03', name: 'Organic Whole Milk', category: 'Dairy', currentStock: 24000, unit: 'ml', minThreshold: 12000, costPerUnit: '$0.002/ml', status: 'OPTIMAL' },
  { id: 'ING-04', name: 'Madagascar Vanilla Syrup', category: 'Syrups', currentStock: 650, unit: 'ml', minThreshold: 1000, costPerUnit: '$0.015/ml', status: 'LOW' },
  { id: 'ING-05', name: 'Laminated Butter Croissant Dough', category: 'Bakery', currentStock: 48, unit: 'units', minThreshold: 20, costPerUnit: '$1.10/ea', status: 'OPTIMAL' },
  { id: 'ING-06', name: 'Country Sourdough Loaves', category: 'Bakery', currentStock: 14, unit: 'loaves', minThreshold: 5, costPerUnit: '$2.50/ea', status: 'OPTIMAL' },
];

export default function InventoryPage(): React.JSX.Element {
  const [ingredients, setIngredients] = useState<IngredientStock[]>(INITIAL_INGREDIENTS);
  const [selectedBOM, setSelectedBOM] = useState<'flat-white' | 'latte' | 'avo-toast'>('flat-white');
  const [poNotice, setPoNotice] = useState<string | null>(null);
  const [isDeliveryModalOpen, setIsDeliveryModalOpen] = useState(false);

  const bomRecipes = {
    'flat-white': {
      title: 'Signature Flat White (12 oz)',
      sku: 'BEV-FW',
      lines: [
        { ingredient: 'Ethiopian Yirgacheffe Beans', qty: '18.0 g', cost: '$0.43' },
        { ingredient: 'Organic Whole Milk (or Oat)', qty: '220.0 ml', cost: '$0.44' },
        { ingredient: 'Compostable 12oz Cup & Lid', qty: '1.0 unit', cost: '$0.18' },
      ],
      totalCost: '$1.05',
      retailPrice: '$4.50',
      margin: '76.7%',
    },
    latte: {
      title: 'Artisan Caffè Latte (16 oz)',
      sku: 'BEV-LAT',
      lines: [
        { ingredient: 'Ethiopian Yirgacheffe Beans', qty: '18.0 g', cost: '$0.43' },
        { ingredient: 'Organic Whole Milk', qty: '320.0 ml', cost: '$0.64' },
        { ingredient: 'Compostable 16oz Cup & Lid', qty: '1.0 unit', cost: '$0.22' },
      ],
      totalCost: '$1.29',
      retailPrice: '$4.75',
      margin: '72.8%',
    },
    'avo-toast': {
      title: 'Avocado Sourdough Toast',
      sku: 'KIT-AVO',
      lines: [
        { ingredient: 'Country Sourdough Loaf (Slices)', qty: '2.0 slices', cost: '$0.62' },
        { ingredient: 'Hass Avocado', qty: '1.0 unit', cost: '$1.20' },
        { ingredient: 'Dukkah Spice & Olive Oil', qty: '15.0 ml', cost: '$0.35' },
      ],
      totalCost: '$2.17',
      retailPrice: '$9.50',
      margin: '77.2%',
    },
  };

  const currentRecipe = bomRecipes[selectedBOM];

  const handleConfirmDelivery = (ingId: string, qty: number, supplier: string, poRef: string) => {
    setIngredients((prev) =>
      prev.map((item) => {
        if (item.id !== ingId) return item;
        const newStock = item.currentStock + qty;
        const newStatus = newStock >= item.minThreshold ? 'OPTIMAL' : 'LOW';
        return { ...item, currentStock: newStock, status: newStatus };
      })
    );
    const targetItem = ingredients.find((i) => i.id === ingId);
    setPoNotice(
      `✓ Restocked ${qty.toLocaleString()} ${targetItem?.unit || 'units'} of ${targetItem?.name} via ${poRef} from ${supplier}. Stock updated to OPTIMAL.`
    );
  };

  return (
    <div className="nx-page-shell" style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px 20px 48px' }}>
      <NexusStack gap="var(--nx-space-6)">
        {/* Header */}
        <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
          <div>
            <NexusText variant="h1">Café Inventory & Recipe BOM</NexusText>
            <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
              Real-time stock decrement upon POS settlement, automated ingredient depletion, and recipe unit margins.
            </NexusText>
          </div>
          <NexusButton variant="primary" size="sm" onClick={() => setIsDeliveryModalOpen(true)}>
            + Receive Delivery PO
          </NexusButton>
        </NexusStack>

        {poNotice && (
          <NexusCard elevation="card" style={{ padding: '10px 16px', backgroundColor: 'var(--nx-surface-selected)' }}>
            <NexusStack direction="row" align="center" justify="space-between">
              <NexusText variant="label">{poNotice}</NexusText>
              <NexusButton variant="ghost" size="sm" onClick={() => setPoNotice(null)}>
                Dismiss
              </NexusButton>
            </NexusStack>
          </NexusCard>
        )}

        {/* Recipe BOM Simulator */}
        <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
          <NexusStack gap="var(--nx-space-4)">
            <NexusStack direction="row" align="center" justify="space-between">
              <div>
                <NexusText variant="h3">Auto-Depletion Recipe BOM</NexusText>
                <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
                  Atomic deduction on counter POS checkout
                </NexusText>
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                {(['flat-white', 'latte', 'avo-toast'] as const).map((r) => (
                  <NexusButton
                    key={r}
                    variant={selectedBOM === r ? 'primary' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedBOM(r)}
                  >
                    {bomRecipes[r].title.split(' (')[0]}
                  </NexusButton>
                ))}
              </div>
            </NexusStack>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px', padding: '16px', borderRadius: '10px', backgroundColor: 'var(--nx-surface-subtle)', border: '1px solid var(--nx-border-subtle)' }}>
              <div>
                <NexusText variant="caption" role="muted">Menu Product</NexusText>
                <NexusText variant="label" style={{ fontWeight: 700, display: 'block' }}>{currentRecipe.title}</NexusText>
                <NexusText variant="caption" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-text-muted)' }}>{currentRecipe.sku}</NexusText>
              </div>
              <div>
                <NexusText variant="caption" role="muted">Cost vs Retail</NexusText>
                <NexusText variant="label" style={{ fontWeight: 700, color: 'var(--nx-status-success)' }}>{currentRecipe.totalCost}</NexusText>
                <NexusText variant="caption" role="muted"> of {currentRecipe.retailPrice}</NexusText>
              </div>
              <div>
                <NexusText variant="caption" role="muted">Gross Margin</NexusText>
                <NexusText variant="h3" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-action-primary)' }}>{currentRecipe.margin}</NexusText>
                <NexusBadge variant="success" label="Healthy Margin" />
              </div>
            </div>

            <table className="nx-data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--nx-border-default)', textAlign: 'left' }}>
                  <th style={{ padding: '8px 12px' }}>Ingredient</th>
                  <th style={{ padding: '8px 12px' }}>Dose / Consumption</th>
                  <th style={{ padding: '8px 12px' }}>Ingredient Unit Cost</th>
                </tr>
              </thead>
              <tbody>
                {currentRecipe.lines.map((l) => (
                  <tr key={l.ingredient} style={{ borderBottom: '1px solid var(--nx-border-subtle)' }}>
                    <td style={{ padding: '8px 12px' }}>{l.ingredient}</td>
                    <td style={{ padding: '8px 12px', fontWeight: 700, color: 'var(--nx-action-primary)' }}>{l.qty}</td>
                    <td style={{ padding: '8px 12px' }}>{l.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </NexusStack>
        </NexusCard>

        {/* Raw Ingredients Stock Ledger */}
        <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
          <NexusStack gap="var(--nx-space-4)">
            <NexusStack direction="row" align="center" justify="space-between">
              <NexusText variant="h3">Raw Ingredients & Dry Goods</NexusText>
              <NexusBadge variant="neutral" label="6 Tracked SKUs" />
            </NexusStack>

            <table className="nx-data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--nx-border-default)', textAlign: 'left' }}>
                  <th style={{ padding: '10px 12px' }}>SKU</th>
                  <th style={{ padding: '10px 12px' }}>Ingredient Name</th>
                  <th style={{ padding: '10px 12px' }}>Available On-Hand</th>
                  <th style={{ padding: '10px 12px' }}>Cost Basis</th>
                  <th style={{ padding: '10px 12px' }}>Stock Health</th>
                </tr>
              </thead>
              <tbody>
                {ingredients.map((ing) => (
                  <tr key={ing.id} style={{ borderBottom: '1px solid var(--nx-border-subtle)' }}>
                    <td style={{ padding: '10px 12px', color: 'var(--nx-text-muted)', fontFamily: 'var(--font-mono, monospace)' }}>{ing.id}</td>
                    <td style={{ padding: '10px 12px', fontWeight: 600 }}>{ing.name}</td>
                    <td style={{ padding: '10px 12px', fontWeight: 700, color: 'var(--nx-action-primary)', fontFamily: 'var(--font-mono, monospace)' }}>
                      {ing.currentStock.toLocaleString()} {ing.unit}
                    </td>
                    <td style={{ padding: '10px 12px' }}>{ing.costPerUnit}</td>
                    <td style={{ padding: '10px 12px' }}>
                      <NexusBadge
                        variant={ing.status === 'OPTIMAL' ? 'success' : ing.status === 'LOW' ? 'warning' : 'danger'}
                        label={ing.status}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </NexusStack>
        </NexusCard>
      </NexusStack>

      <ReceiveDeliveryModal
        isOpen={isDeliveryModalOpen}
        onClose={() => setIsDeliveryModalOpen(false)}
        onConfirmDelivery={handleConfirmDelivery}
        availableIngredients={ingredients.map((i) => ({ id: i.id, name: i.name, unit: i.unit }))}
      />
    </div>
  );
}
