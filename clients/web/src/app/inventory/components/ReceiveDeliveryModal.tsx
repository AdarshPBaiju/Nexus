'use client';

import React, { useState } from 'react';
import {
  NexusBox,
  NexusButton,
  NexusCard,
  NexusSelect,
  NexusStack,
  NexusText,
  NexusTextInput,
} from '@nexus/ui';

export interface ReceiveDeliveryModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onConfirmDelivery: (ingredientId: string, quantity: number, supplier: string, poRef: string) => void;
  readonly availableIngredients: readonly { id: string; name: string; unit: string }[];
}

export function ReceiveDeliveryModal({
  isOpen,
  onClose,
  onConfirmDelivery,
  availableIngredients,
}: ReceiveDeliveryModalProps): React.JSX.Element | null {
  const [selectedIngredient, setSelectedIngredient] = useState<string>(availableIngredients[1]?.id || 'ING-02');
  const [quantity, setQuantity] = useState<string>('5000');
  const [supplier, setSupplier] = useState<string>('Oatly UK Wholesale Distro');
  const [poRef, setPoRef] = useState<string>('PO-2026-9021');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = () => {
    const qtyNum = parseFloat(quantity);
    if (isNaN(qtyNum) || qtyNum <= 0) return;
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      onConfirmDelivery(selectedIngredient, qtyNum, supplier, poRef);
      onClose();
    }, 400);
  };

  const selectedItem = availableIngredients.find((i) => i.id === selectedIngredient);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="receive-delivery-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1100,
        padding: '16px',
      }}
    >
      <NexusCard
        elevation="elevated"
        style={{
          width: '100%',
          maxWidth: '520px',
          padding: '24px',
          backgroundColor: 'var(--nx-surface-card)',
          border: '1px solid var(--nx-border-default)',
          borderRadius: '14px',
          boxShadow: 'var(--nx-shadow-lg)',
        }}
      >
        <NexusStack gap="18px">
          {/* Header */}
          <NexusStack direction="row" align="center" justify="space-between">
            <div>
              <NexusText variant="h3" style={{ fontWeight: 700 }}>
                Receive Supplier Delivery PO
              </NexusText>
              <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
                Atomic stock increment & FIFO batch cost tracking
              </NexusText>
            </div>
            <NexusButton variant="ghost" size="sm" onClick={onClose} ariaLabel="Close">
              ✕
            </NexusButton>
          </NexusStack>

          <NexusStack gap="14px">
            <NexusTextInput
              labelKey="PO Reference Number"
              value={poRef}
              onChange={(val: string) => setPoRef(val)}
              placeholderKey="PO-2026-9021"
            />

            <NexusTextInput
              labelKey="Supplier Entity Name"
              value={supplier}
              onChange={(val: string) => setSupplier(val)}
              placeholderKey="Oatly UK Wholesale Distro"
            />

            <NexusSelect
              labelKey="Select Delivered Ingredient"
              value={selectedIngredient}
              onChange={(val: string) => setSelectedIngredient(val)}
              options={availableIngredients.map((i) => ({
                value: i.id,
                label: `${i.name} (${i.unit})`,
              }))}
            />

            <NexusTextInput
              labelKey={`Quantity Received (${selectedItem?.unit || 'units'})`}
              value={quantity}
              onChange={(val: string) => setQuantity(val)}
              placeholderKey="5000"
            />
          </NexusStack>

          {/* Action Buttons */}
          <NexusStack direction="row" justify="end" gap="10px" style={{ paddingTop: '8px' }}>
            <NexusButton variant="secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </NexusButton>
            <NexusButton variant="primary" onClick={handleSubmit} disabled={isSubmitting}>
              {isSubmitting ? 'Restocking Inventory...' : 'Confirm Delivery & Restock'}
            </NexusButton>
          </NexusStack>
        </NexusStack>
      </NexusCard>
    </div>
  );
}
