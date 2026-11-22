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
    <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
        <NexusStack gap="var(--nx-space-1)">
          <NexusText variant="h1">Tenant Lifecycle & Onboarding</NexusText>
          <NexusText variant="body" role="secondary">
            Register a new tenant organization, configure regional RLS boundaries, and pre-seed the café catalog.
          </NexusText>
        </NexusStack>
        <NexusBadge variant="info" label={`STEP ${step} OF 4`} />
      </NexusStack>

      {isActivated ? (
        <NexusCard elevation="card" style={{ padding: 'var(--nx-space-6)', textAlign: 'center' }}>
          <div className="flex flex-col items-center space-y-4">
            <div
              className="w-16 h-16 rounded-3xl flex items-center justify-center"
              style={{
                backgroundColor: 'var(--nx-status-success-subtle)',
                color: 'var(--nx-status-success-text)',
                border: '1px solid color-mix(in srgb, var(--nx-status-success) 30%, transparent)',
              }}
            >
              <NexusGlyph name="verified" size={36} color="var(--nx-status-success-text)" />
            </div>
            <div>
              <NexusText variant="h2">Tenant Activated & Ready</NexusText>
              <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '4px' }}>
                PostgreSQL 16 Forced RLS Tenant UUID: 7e89a1b2-c3d4-4e5f-a6b7-c8d9e0f1a2b3
              </NexusText>
            </div>
            <div className="w-full max-w-md p-4 rounded-xl bg-[var(--nx-surface-subtle)] border border-[var(--nx-border-default)] text-left font-mono text-xs space-y-2">
              <div className="flex justify-between text-[var(--nx-text-muted)]">
                <span>Organization:</span>
                <span className="text-[var(--nx-text-primary)] font-bold">{businessName}</span>
              </div>
              <div className="flex justify-between text-[var(--nx-text-muted)]">
                <span>Subdomain Slug:</span>
                <span className="text-[var(--nx-status-info-text)] font-bold">{slug}.nexus.app</span>
              </div>
              <div className="flex justify-between text-[var(--nx-text-muted)]">
                <span>Assigned Branch:</span>
                <span className="text-[var(--nx-text-primary)]">{branchName}</span>
              </div>
              <div className="flex justify-between text-[var(--nx-text-muted)]">
                <span>Pre-Seeded Catalog:</span>
                <span className="text-[var(--nx-status-success-text)] font-bold">14 Items & BOM Recipes</span>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <Link href="/pos">
                <NexusButton variant="primary" size="lg">
                  Launch Counter POS →
                </NexusButton>
              </Link>
              <Link href="/">
                <NexusButton variant="outline" size="lg">
                  Open Mission Control
                </NexusButton>
              </Link>
            </div>
          </div>
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
                  onChange={(v) => {
                    setBusinessName(v);
                    setSlug(v.toLowerCase().replace(/[^a-z0-9]/g, '-'));
                  }}
                  placeholderKey="e.g. Artisan Coffee Roasters"
                  isRequired
                />
                <NexusTextInput
                  labelKey="Subdomain Slug (.nexus.app)"
                  value={slug}
                  onChange={setSlug}
                  placeholderKey="artisan-coffee"
                  isRequired
                />
              </NexusStack>
            )}

            {step === 2 && (
              <NexusStack gap="var(--nx-space-4)">
                <NexusText variant="h3">Step 2: Initial Branch & Counter Workstation</NexusText>
                <NexusTextInput
                  labelKey="Primary Branch Name"
                  value={branchName}
                  onChange={setBranchName}
                  placeholderKey="e.g. Flagship Roastery HQ"
                  isRequired
                />
                <NexusNumberInput
                  labelKey="Cash Drawer Opening Float ($)"
                  value={openingFloat}
                  onChange={setOpeningFloat}
                  min={0}
                  step={10}
                />
              </NexusStack>
            )}

            {step === 3 && (
              <NexusStack gap="var(--nx-space-4)">
                <NexusText variant="h3">Step 3: Choose Your Subscription Plan</NexusText>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {[
                    { id: 'STARTER', name: 'Starter', price: '$49/mo' },
                    { id: 'PRO', name: 'Artisan Pro', price: '$149/mo' },
                    { id: 'ENTERPRISE', name: 'Enterprise', price: '$499/mo' },
                  ].map((p) => (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => setSelectedPlan(p.id)}
                      className={`p-3 rounded-xl border text-center transition-all ${
                        selectedPlan === p.id
                          ? 'border-[var(--nx-action-primary)] bg-[var(--nx-surface-selected)] text-[var(--nx-text-primary)] shadow-[var(--nx-shadow-sm)]'
                          : 'border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]'
                      }`}
                    >
                      <span className="text-xs font-bold block">{p.name}</span>
                      <span className="text-sm font-mono font-bold text-[var(--nx-action-primary)] mt-1 block">{p.price}</span>
                    </button>
                  ))}
                </div>
              </NexusStack>
            )}

            {step === 4 && (
              <NexusStack gap="var(--nx-space-4)">
                <NexusText variant="h3">Step 4: Pre-Seed Specialty Café Template</NexusText>
                <div className="p-4 rounded-xl bg-[var(--nx-surface-subtle)] border border-[var(--nx-border-default)] space-y-2 text-xs">
                  <div className="flex items-center gap-2 font-semibold text-[var(--nx-text-primary)]">
                    <NexusGlyph name="local_cafe" size={20} color="var(--nx-action-primary)" />
                    <span>Artisan Roastery & Café Template</span>
                  </div>
                  <p className="text-[var(--nx-text-secondary)]">
                    Installs 14 curated specialty coffee items, milk modifiers (Oat, Almond), cup sizes, recipe BOM auto-depletions, and cashier PINs.
                  </p>
                </div>
              </NexusStack>
            )}

            <div className="flex justify-between items-center pt-4 border-t border-[var(--nx-border-default)]">
              <NexusButton
                variant="ghost"
                size="sm"
                disabled={step === 1}
                onClick={() => setStep(step - 1)}
              >
                &larr; Back
              </NexusButton>
              <NexusButton variant="primary" size="md" onClick={handleNext}>
                {step === 4 ? 'Activate Tenant & Launch →' : 'Continue →'}
              </NexusButton>
            </div>
          </NexusStack>
        </NexusCard>
      )}
    </NexusStack>
  );
}
