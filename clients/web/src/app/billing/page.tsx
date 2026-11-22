'use client';

import React, { useState } from 'react';
import {
  NexusBadge,
  NexusButton,
  NexusCard,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { BillingQuotaMeters } from './components/BillingQuotaMeters';
import { BillingInvoicesTable } from './components/BillingInvoicesTable';

export default function BillingPage(): React.JSX.Element {
  const [statusNotice, setStatusNotice] = useState<string | null>(null);

  const pastInvoices = [
    { id: 'INV-2026-11', date: 'Nov 01, 2026', amount: '$149.00', card: 'Visa ···· 4242', hash: 'e3b0c442...855' },
    { id: 'INV-2026-10', date: 'Oct 01, 2026', amount: '$149.00', card: 'Visa ···· 4242', hash: '9f86d081...001' },
    { id: 'INV-2026-09', date: 'Sep 01, 2026', amount: '$149.00', card: 'Visa ···· 4242', hash: '5e884898...233' },
  ];

  return (
    <div className="nx-page-shell" style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px 20px 48px' }}>
      <NexusStack gap="var(--nx-space-6)">
        {/* Header */}
        <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
          <div>
            <NexusText variant="h1">Cloud SaaS Subscription & Quotas</NexusText>
            <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
              Multi-tenant regional cloud quotas, station licenses, and WORM-compliant fiscal statements.
            </NexusText>
          </div>
          <NexusBadge variant="success" label="Active Subscription: PRO" />
        </NexusStack>

        {statusNotice && (
          <NexusCard elevation="card" style={{ padding: '10px 16px', backgroundColor: 'var(--nx-surface-selected)' }}>
            <NexusStack direction="row" align="center" justify="space-between">
              <NexusText variant="label">{statusNotice}</NexusText>
              <NexusButton variant="ghost" size="sm" onClick={() => setStatusNotice(null)}>
                Dismiss
              </NexusButton>
            </NexusStack>
          </NexusCard>
        )}

        {/* Current Tier & Live Quotas */}
        <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
          <NexusStack gap="var(--nx-space-4)">
            <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <NexusText variant="h3">Current Plan: Professional Tier ($149/mo)</NexusText>
                <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
                  Next renewal: December 01, 2026 via Stripe Automated Cloud Invoicing
                </NexusText>
              </div>
              <NexusButton variant="outline" size="sm" onClick={() => setStatusNotice('Payment portal link sent to primary billing admin email.')}>
                Update Card (Visa ···· 4242)
              </NexusButton>
            </NexusStack>

            <BillingQuotaMeters />
          </NexusStack>
        </NexusCard>

        {/* Plan Comparison */}
        <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
          <NexusStack gap="var(--nx-space-4)">
            <NexusText variant="h3">Tier Comparison & Lifecycle Management</NexusText>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              {[
                { id: 'STARTER', name: 'Café Starter', price: '$49/mo', desc: 'Single counter POS, basic shift register, up to 3 staff members.', active: false },
                { id: 'PRO', name: 'Artisan Pro', price: '$149/mo', desc: 'Up to 10 POS stations, KDS Barista Canvas, Recipe BOM, Multi-tender.', active: true },
                { id: 'ENTERPRISE', name: 'Roastery Enterprise', price: '$499/mo', desc: 'Multi-branch regional RLS, 24/7 dedicated support, custom tax slabs.', active: false },
              ].map((tier) => (
                <div
                  key={tier.id}
                  style={{
                    padding: '16px',
                    borderRadius: '10px',
                    border: `1px solid ${tier.active ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                    backgroundColor: tier.active ? 'var(--nx-surface-selected)' : 'var(--nx-surface-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                      <NexusText variant="label" style={{ fontWeight: 700 }}>{tier.name}</NexusText>
                      {tier.active && <NexusBadge variant="success" label="CURRENT" />}
                    </div>
                    <NexusText variant="h2" style={{ fontFamily: 'var(--font-mono, monospace)', color: 'var(--nx-action-primary)' }}>
                      {tier.price}
                    </NexusText>
                    <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '8px' }}>
                      {tier.desc}
                    </NexusText>
                  </div>
                  <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--nx-border-default)' }}>
                    <NexusButton
                      variant={tier.active ? 'outline' : 'primary'}
                      size="sm"
                      onClick={() => setStatusNotice(tier.active ? 'Plan management link sent to email.' : `Upgrading to ${tier.name}...`)}
                      style={{ width: '100%', justifyContent: 'center' }}
                    >
                      {tier.active ? 'Manage Plan' : 'Upgrade →'}
                    </NexusButton>
                  </div>
                </div>
              ))}
            </div>
          </NexusStack>
        </NexusCard>

        {/* Past Invoices Table */}
        <BillingInvoicesTable
          invoices={pastInvoices}
          onDownload={(invId) => setStatusNotice(`Preparing WORM PDF invoice download for ${invId}…`)}
        />
      </NexusStack>
    </div>
  );
}
