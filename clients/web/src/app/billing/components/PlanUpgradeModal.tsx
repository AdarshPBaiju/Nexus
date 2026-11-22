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

export interface PlanUpgradeModalProps {
  readonly isOpen: boolean;
  readonly onClose: () => void;
  readonly onUpgradeSuccess: (planId: string, planName: string, extraStations: number) => void;
}

export function PlanUpgradeModal({
  isOpen,
  onClose,
  onUpgradeSuccess,
}: PlanUpgradeModalProps): React.JSX.Element | null {
  const [selectedPlan, setSelectedPlan] = useState<'STARTER' | 'PRO' | 'ENTERPRISE'>('PRO');
  const [interval, setInterval] = useState<'MONTHLY' | 'ANNUAL'>('ANNUAL');
  const [extraStations, setExtraStations] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen) return null;

  const plans = {
    STARTER: { name: 'Café Starter', basePrice: 49, stations: 3, kds: 1 },
    PRO: { name: 'Artisan Pro', basePrice: 149, stations: 10, kds: 5 },
    ENTERPRISE: { name: 'Roastery Enterprise', basePrice: 499, stations: 25, kds: 12 },
  };

  const plan = plans[selectedPlan];
  const monthlyMultiplier = interval === 'ANNUAL' ? 0.8 : 1.0;
  const planCost = Math.round(plan.basePrice * monthlyMultiplier);
  const stationCost = extraStations * 29;
  const totalMonthly = planCost + stationCost;

  const handleConfirm = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      onUpgradeSuccess(selectedPlan, plan.name, extraStations);
      onClose();
    }, 600);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="upgrade-plan-title"
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
          maxWidth: '540px',
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
                Manage Cloud Subscription
              </NexusText>
              <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
                Instant quota provisioning across regional cell clusters
              </NexusText>
            </div>
            <NexusButton variant="ghost" size="sm" onClick={onClose} ariaLabel="Close">
              ✕
            </NexusButton>
          </NexusStack>

          {/* Billing Interval Toggle */}
          <div
            style={{
              display: 'flex',
              padding: '3px',
              borderRadius: '8px',
              backgroundColor: 'var(--nx-surface-subtle)',
              border: '1px solid var(--nx-border-subtle)',
            }}
          >
            <button
              type="button"
              onClick={() => setInterval('MONTHLY')}
              style={{
                flex: 1,
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: interval === 'MONTHLY' ? 'var(--nx-surface-card)' : 'transparent',
                color: 'var(--nx-text-primary)',
                fontWeight: interval === 'MONTHLY' ? 700 : 500,
                cursor: 'pointer',
                fontSize: '12px',
              }}
            >
              Monthly Billing
            </button>
            <button
              type="button"
              onClick={() => setInterval('ANNUAL')}
              style={{
                flex: 1,
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: interval === 'ANNUAL' ? 'var(--nx-surface-card)' : 'transparent',
                color: 'var(--nx-text-primary)',
                fontWeight: interval === 'ANNUAL' ? 700 : 500,
                cursor: 'pointer',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
              }}
            >
              <span>Annual Billing</span>
              <NexusBadge variant="success" label="20% OFF" />
            </button>
          </div>

          {/* Plan Selector Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
            {(['STARTER', 'PRO', 'ENTERPRISE'] as const).map((id) => {
              const p = plans[id];
              const isSelected = selectedPlan === id;
              const price = Math.round(p.basePrice * monthlyMultiplier);
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setSelectedPlan(id)}
                  style={{
                    padding: '12px 10px',
                    borderRadius: '8px',
                    border: `1px solid ${isSelected ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                    backgroundColor: isSelected ? 'var(--nx-surface-selected)' : 'var(--nx-surface-subtle)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <NexusText variant="caption" style={{ fontWeight: isSelected ? 700 : 500, display: 'block' }}>
                    {p.name}
                  </NexusText>
                  <NexusText variant="h3" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-action-primary)', marginTop: '4px' }}>
                    ${price}<span style={{ fontSize: '11px', color: 'var(--nx-text-muted)' }}>/mo</span>
                  </NexusText>
                  <NexusText variant="caption" role="muted" style={{ fontSize: '10px', display: 'block', marginTop: '4px' }}>
                    {p.stations} POS · {p.kds} KDS
                  </NexusText>
                </button>
              );
            })}
          </div>

          {/* Add-on POS Stations */}
          <NexusBox style={{ padding: '12px 14px', borderRadius: '8px', backgroundColor: 'var(--nx-surface-subtle)', border: '1px solid var(--nx-border-subtle)' }}>
            <NexusStack direction="row" align="center" justify="space-between">
              <div>
                <NexusText variant="label" style={{ fontWeight: 600 }}>Additional POS Counter Stations</NexusText>
                <NexusText variant="caption" role="muted" style={{ display: 'block' }}>
                  $29/station/mo · Hardware bridge license included
                </NexusText>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <NexusButton variant="outline" size="sm" onClick={() => setExtraStations((p) => Math.max(p - 1, 0))}>
                  -
                </NexusButton>
                <NexusText variant="label" style={{ fontFamily: 'var(--font-mono, monospace)', minWidth: '24px', textAlign: 'center' }}>
                  +{extraStations}
                </NexusText>
                <NexusButton variant="outline" size="sm" onClick={() => setExtraStations((p) => p + 1)}>
                  +
                </NexusButton>
              </div>
            </NexusStack>
          </NexusBox>

          {/* Total & Payment Summary */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '4px' }}>
            <div>
              <NexusText variant="caption" role="muted">Total Monthly Charge</NexusText>
              <NexusText variant="h2" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-action-primary)', margin: 0 }}>
                ${totalMonthly}<span style={{ fontSize: '12px', color: 'var(--nx-text-muted)' }}>/month</span>
              </NexusText>
            </div>
            <NexusBadge variant="neutral" label="Card: Visa ···· 4242" />
          </div>

          {/* Action Buttons */}
          <NexusStack direction="row" justify="end" gap="10px" style={{ paddingTop: '8px' }}>
            <NexusButton variant="secondary" onClick={onClose} disabled={isProcessing}>
              Cancel
            </NexusButton>
            <NexusButton variant="primary" onClick={handleConfirm} disabled={isProcessing}>
              {isProcessing ? 'Activating Subscription...' : 'Confirm Subscription Upgrade'}
            </NexusButton>
          </NexusStack>
        </NexusStack>
      </NexusCard>
    </div>
  );
}
