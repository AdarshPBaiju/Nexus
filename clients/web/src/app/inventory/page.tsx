'use client';

import React, { useState } from 'react';
import {
  NexusBadge,
  NexusBox,
  NexusButton,
  NexusCard,
  NexusStack,
  NexusText,
} from '@nexus/ui';

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

  const bomRecipes = {
    'flat-white': {
      title: 'Signature Flat White (12 oz)',
      sku: 'BEV-FW',
      yield: '1 Cup',
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
      yield: '1 Cup',
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
      yield: '1 Plate',
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

  return (
    <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
        <NexusStack gap="var(--nx-space-1)">
          <NexusText variant="h1">Café Inventory & Recipe BOM</NexusText>
          <NexusText variant="body" role="secondary">
            Real-time stock decrement upon POS settlement, automated ingredient depletion, and recipe unit margins.
          </NexusText>
        </NexusStack>
        <NexusButton variant="primary" size="sm" onClick={() => setPoNotice('PO Intake modal: Supplier PO-9021 delivery draft created.')}>
          + Receive Delivery PO
        </NexusButton>
      </NexusStack>

      {poNotice && (
        <NexusCard elevation="card" style={{ padding: '8px 14px', backgroundColor: 'var(--nx-surface-selected)' }}>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="label">{poNotice}</NexusText>
            <NexusButton variant="ghost" size="sm" onClick={() => setPoNotice(null)}>
              Dismiss
            </NexusButton>
          </NexusStack>
        </NexusCard>
      )}

      {/* Recipe Bill of Materials Simulator */}
      <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
        <NexusStack gap="var(--nx-space-4)">
          <NexusStack direction="row" align="center" justify="space-between">
            <div>
              <NexusText variant="h3">Auto-Depletion Recipe BOM</NexusText>
              <NexusText variant="caption" role="muted">Atomic deduction on counter POS purchase</NexusText>
            </div>
            <div className="flex gap-1.5">
              {(['flat-white', 'latte', 'avo-toast'] as const).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setSelectedBOM(r)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                    selectedBOM === r ? 'bg-primary text-on-primary' : 'bg-surface-container text-outline'
                  }`}
                >
                  {bomRecipes[r].title.split(' (')[0]}
                </button>
              ))}
            </div>
          </NexusStack>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-xl bg-surface-container border border-surface-container-highest">
            <div>
              <span className="text-xs text-outline block">Menu Product</span>
              <span className="text-sm font-bold text-on-surface">{currentRecipe.title}</span>
              <span className="text-xs font-mono text-outline block">{currentRecipe.sku}</span>
            </div>
            <div className="font-mono">
              <span className="text-xs text-outline block">Cost vs Retail</span>
              <span className="text-sm font-bold text-emerald-400">{currentRecipe.totalCost}</span>
              <span className="text-xs text-outline"> of {currentRecipe.retailPrice}</span>
            </div>
            <div>
              <span className="text-xs text-outline block">Gross Margin</span>
              <span className="text-base font-bold text-primary font-mono">{currentRecipe.margin}</span>
              <NexusBadge variant="success" label="Healthy Margin" />
            </div>
          </div>

          {/* BOM Lines */}
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left">
              <thead>
                <tr className="border-b border-surface-container-highest text-outline">
                  <th className="py-2 px-3">Ingredient</th>
                  <th className="py-2 px-3">Dose / Consumption</th>
                  <th className="py-2 px-3">Ingredient Unit Cost</th>
                </tr>
              </thead>
              <tbody>
                {currentRecipe.lines.map((l) => (
                  <tr key={l.ingredient} className="border-b border-surface-container-highest/60 text-on-surface">
                    <td className="py-2.5 px-3 font-sans font-medium">{l.ingredient}</td>
                    <td className="py-2.5 px-3 font-bold text-primary">{l.qty}</td>
                    <td className="py-2.5 px-3">{l.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </NexusStack>
      </NexusCard>

      {/* Raw Ingredients Stock Ledger */}
      <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
        <NexusStack gap="var(--nx-space-4)">
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="h3">Raw Ingredients & Dry Goods</NexusText>
            <NexusBadge variant="neutral" label="6 Tracked SKUs" />
          </NexusStack>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-surface-container-highest text-outline font-mono">
                  <th className="py-2 px-3">SKU</th>
                  <th className="py-2 px-3">Ingredient Name</th>
                  <th className="py-2 px-3">Available On-Hand</th>
                  <th className="py-2 px-3">Cost Basis</th>
                  <th className="py-2 px-3">Stock Health</th>
                </tr>
              </thead>
              <tbody>
                {ingredients.map((ing) => (
                  <tr key={ing.id} className="border-b border-surface-container-highest/60 text-on-surface font-mono">
                    <td className="py-3 px-3 text-outline">{ing.id}</td>
                    <td className="py-3 px-3 font-sans font-semibold">{ing.name}</td>
                    <td className="py-3 px-3 font-bold text-primary">
                      {ing.currentStock.toLocaleString()} {ing.unit}
                    </td>
                    <td className="py-3 px-3">{ing.costPerUnit}</td>
                    <td className="py-3 px-3">
                      <NexusBadge
                        variant={ing.status === 'OPTIMAL' ? 'success' : ing.status === 'LOW' ? 'warning' : 'danger'}
                        label={ing.status}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </NexusStack>
      </NexusCard>
    </NexusStack>
  );
}
