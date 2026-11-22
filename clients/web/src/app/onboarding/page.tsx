'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  NexusBadge,
  NexusButton,
  NexusCard,
  NexusNumberInput,
  NexusStack,
  NexusText,
  NexusTextInput,
} from '@nexus/ui';
import { NexusGlyph } from '../components/NexusGlyph';

export default function OnboardingPage(): React.JSX.Element {
  const [step, setStep] = useState<number>(1);
  const [businessName, setBusinessName] = useState('Artisan Coffee Roasters');
  const [slug, setSlug] = useState('artisan-coffee');
  const [branchName, setBranchName] = useState('London SoHo Roastery');
  const [openingFloat, setOpeningFloat] = useState(200);
  const [selectedPlan, setSelectedPlan] = useState('PRO');
  const [isActivated, setIsActivated] = useState(false);

  const handleNext = () => {
    if (step < 4) setStep(step + 1);
    else setIsActivated(true);
  };

  return (
    <div className="nx-page-shell" style={{ maxWidth: '800px', margin: '0 auto', padding: '24px 20px 48px' }}>
      <NexusStack gap="var(--nx-space-6)">
        <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
          <div>
            <NexusText variant="h1">Store Lifecycle & Terminal Setup</NexusText>
            <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
              Configure your store profile, counter terminals, cash drawer opening float, and catalog BOM templates.
            </NexusText>
          </div>
          <NexusBadge variant="info" label={`STEP ${step} OF 4`} />
        </NexusStack>

        {isActivated ? (
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-6)', textAlign: 'center' }}>
            <NexusStack gap="18px" align="center">
              <div
                style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '16px',
                  backgroundColor: 'var(--nx-status-success-subtle)',
                  color: 'var(--nx-status-success-text)',
                  border: '1px solid var(--nx-status-success)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <NexusGlyph name="verified" size={36} color="var(--nx-status-success-text)" />
              </div>
              <div>
                <NexusText variant="h2">Store Cell Activated & Ready</NexusText>
                <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '4px' }}>
                  PostgreSQL 16 Forced RLS Tenant UUID: 7e89a1b2-c3d4-4e5f-a6b7-c8d9e0f1a2b3
                </NexusText>
              </div>

              <div
                style={{
                  width: '100%',
                  maxWidth: '440px',
                  padding: '16px',
                  borderRadius: '10px',
                  backgroundColor: 'var(--nx-surface-subtle)',
                  border: '1px solid var(--nx-border-default)',
                  textAlign: 'left',
                }}
              >
                <NexusStack gap="8px">
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <NexusText variant="caption" role="muted">Organization:</NexusText>
                    <NexusText variant="caption" style={{ fontWeight: 700 }}>{businessName}</NexusText>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <NexusText variant="caption" role="muted">Subdomain Slug:</NexusText>
                    <NexusText variant="caption" style={{ fontWeight: 700, color: 'var(--nx-action-primary)' }}>{slug}.nexus-qsr.io</NexusText>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <NexusText variant="caption" role="muted">Assigned Branch:</NexusText>
                    <NexusText variant="caption">{branchName}</NexusText>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <NexusText variant="caption" role="muted">Pre-Seeded Catalog:</NexusText>
                    <NexusBadge variant="success" label="14 Items & BOM Recipes Active" />
                  </div>
                </NexusStack>
              </div>

              <div style={{ display: 'flex', gap: '12px', paddingTop: '8px' }}>
                <Link href="/pos">
                  <NexusButton variant="primary" size="md">
                    Launch Counter POS →
                  </NexusButton>
                </Link>
                <Link href="/">
                  <NexusButton variant="outline" size="md">
                    Open Mission Control
                  </NexusButton>
                </Link>
              </div>
            </NexusStack>
          </NexusCard>
        ) : (
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-6)' }}>
            <NexusStack gap="var(--nx-space-5)">
              {step === 1 && (
                <NexusStack gap="var(--nx-space-4)">
                  <NexusText variant="h3">Step 1: Business Profile & Subdomain</NexusText>
                  <NexusTextInput
                    labelKey="Brand / Café Name"
                    value={businessName}
                    onChange={(v: string) => {
                      setBusinessName(v);
                      setSlug(v.toLowerCase().replace(/[^a-z0-9]/g, '-'));
                    }}
                    placeholderKey="e.g. Artisan Coffee Roasters"
                  />
                  <NexusTextInput
                    labelKey="Subdomain Slug (.nexus-qsr.io)"
                    value={slug}
                    onChange={(v: string) => setSlug(v)}
                    placeholderKey="artisan-coffee"
                  />
                </NexusStack>
              )}

              {step === 2 && (
                <NexusStack gap="var(--nx-space-4)">
                  <NexusText variant="h3">Step 2: Initial Branch & Counter Workstation</NexusText>
                  <NexusTextInput
                    labelKey="Primary Branch Name"
                    value={branchName}
                    onChange={(v: string) => setBranchName(v)}
                    placeholderKey="e.g. Flagship Roastery HQ"
                  />
                  <NexusNumberInput
                    labelKey="Cash Drawer Opening Float ($)"
                    value={openingFloat}
                    onChange={(v: number) => setOpeningFloat(v)}
                    min={0}
                    step={10}
                  />
                </NexusStack>
              )}

              {step === 3 && (
                <NexusStack gap="var(--nx-space-4)">
                  <NexusText variant="h3">Step 3: Choose Your Subscription Plan</NexusText>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                    {[
                      { id: 'STARTER', name: 'Starter', price: '$49/mo' },
                      { id: 'PRO', name: 'Artisan Pro', price: '$149/mo' },
                      { id: 'ENTERPRISE', name: 'Enterprise', price: '$499/mo' },
                    ].map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setSelectedPlan(p.id)}
                        style={{
                          padding: '12px',
                          borderRadius: '10px',
                          border: `1px solid ${selectedPlan === p.id ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                          backgroundColor: selectedPlan === p.id ? 'var(--nx-surface-selected)' : 'var(--nx-surface-subtle)',
                          cursor: 'pointer',
                          textAlign: 'center',
                        }}
                      >
                        <NexusText variant="label" style={{ fontWeight: 700, display: 'block' }}>{p.name}</NexusText>
                        <NexusText variant="h3" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-action-primary)', marginTop: '4px' }}>
                          {p.price}
                        </NexusText>
                      </button>
                    ))}
                  </div>
                </NexusStack>
              )}

              {step === 4 && (
                <NexusStack gap="var(--nx-space-4)">
                  <NexusText variant="h3">Step 4: Pre-Seed Specialty Café Template</NexusText>
                  <div
                    style={{
                      padding: '16px',
                      borderRadius: '10px',
                      backgroundColor: 'var(--nx-surface-subtle)',
                      border: '1px solid var(--nx-border-default)',
                    }}
                  >
                    <NexusStack gap="6px">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <NexusGlyph name="local_cafe" size={20} color="var(--nx-action-primary)" />
                        <NexusText variant="label" style={{ fontWeight: 700 }}>Artisan Roastery & Café Catalog</NexusText>
                      </div>
                      <NexusText variant="caption" role="muted">
                        Installs 14 curated specialty coffee items, milk modifiers (Oat, Almond), cup sizes, recipe BOM auto-depletions, and cashier PINs.
                      </NexusText>
                    </NexusStack>
                  </div>
                </NexusStack>
              )}

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '16px', borderTop: '1px solid var(--nx-border-default)' }}>
                <NexusButton
                  variant="ghost"
                  size="sm"
                  disabled={step === 1}
                  onClick={() => setStep((s) => s - 1)}
                >
                  ← Back
                </NexusButton>
                <NexusButton variant="primary" size="md" onClick={handleNext}>
                  {step === 4 ? 'Activate Store & Launch →' : 'Continue →'}
                </NexusButton>
              </div>
            </NexusStack>
          </NexusCard>
        )}
      </NexusStack>
    </div>
  );
}
