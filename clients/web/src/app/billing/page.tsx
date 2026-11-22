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

export default function BillingPage(): React.JSX.Element {
  const [selectedPlan, setSelectedPlan] = useState<'STARTER' | 'PRO' | 'ENTERPRISE'>('PRO');
  const [statusNotice, setStatusNotice] = useState<string | null>(null);

  const pastInvoices = [
    { id: 'INV-2026-11', date: 'Nov 01, 2026', amount: '$149.00', status: 'PAID', card: 'Visa ···· 4242', hash: 'e3b0c442...855' },
    { id: 'INV-2026-10', date: 'Oct 01, 2026', amount: '$149.00', status: 'PAID', card: 'Visa ···· 4242', hash: '9f86d081...001' },
    { id: 'INV-2026-09', date: 'Sep 01, 2026', amount: '$149.00', status: 'PAID', card: 'Visa ···· 4242', hash: '5e884898...233' },
  ];

  return (
    <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: 'var(--nx-space-3)' }}>
        <NexusStack gap="var(--nx-space-1)">
          <NexusText variant="h1">SaaS Subscription & Billing</NexusText>
          <NexusText variant="body" role="secondary">
            Manage your multi-tenant subscription tiers, workstation quotas, and gapless fiscal billing statements.
          </NexusText>
        </NexusStack>
        <NexusBadge variant="success" label="Active Subscription: PRO" />
      </NexusStack>

      {statusNotice && (
        <NexusCard elevation="card" style={{ padding: '8px 14px', backgroundColor: 'var(--nx-surface-selected)' }}>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="label">{statusNotice}</NexusText>
            <NexusButton variant="ghost" size="sm" onClick={() => setStatusNotice(null)}>
              Dismiss
            </NexusButton>
          </NexusStack>
        </NexusCard>
      )}

      {/* Current Tier & Quotas */}
      <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
        <NexusStack gap="var(--nx-space-4)">
          <NexusStack direction="row" align="center" justify="space-between">
            <div>
              <NexusText variant="h3">Current Plan: Professional Tier ($149/mo)</NexusText>
              <NexusText variant="caption" role="muted">Next renewal: December 01, 2026 via Stripe Automated Billing</NexusText>
            </div>
            <NexusButton variant="outline" size="sm" onClick={() => setStatusNotice('Payment portal link sent to primary billing admin email.')}>
              Update Card (Visa ···· 4242)
            </NexusButton>
          </NexusStack>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 p-4 rounded-xl bg-surface-container border border-surface-container-highest font-mono text-xs">
            <div>
              <span className="text-outline uppercase text-[10px] block">POS Workstations</span>
              <span className="text-base font-bold text-on-surface">3 / 10 Active</span>
              <div className="w-full h-1.5 rounded-full bg-surface-container-highest mt-1">
                <div className="w-[30%] h-full rounded-full bg-primary" />
              </div>
            </div>
            <div>
              <span className="text-outline uppercase text-[10px] block">Monthly Sales Volume</span>
              <span className="text-base font-bold text-emerald-400">$42.8k / $100k</span>
              <div className="w-full h-1.5 rounded-full bg-surface-container-highest mt-1">
                <div className="w-[43%] h-full rounded-full bg-emerald-400" />
              </div>
            </div>
            <div>
              <span className="text-outline uppercase text-[10px] block">Active Staff Roster</span>
              <span className="text-base font-bold text-on-surface">4 / 20 Seats</span>
              <div className="w-full h-1.5 rounded-full bg-surface-container-highest mt-1">
                <div className="w-[20%] h-full rounded-full bg-primary" />
              </div>
            </div>
            <div>
              <span className="text-outline uppercase text-[10px] block">KDS Barista Canvases</span>
              <span className="text-base font-bold text-secondary">1 / 5 Enabled</span>
              <div className="w-full h-1.5 rounded-full bg-surface-container-highest mt-1">
                <div className="w-[20%] h-full rounded-full bg-secondary" />
              </div>
            </div>
          </div>
        </NexusStack>
      </NexusCard>

      {/* Plan Comparison & Upgrades */}
      <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
        <NexusStack gap="var(--nx-space-4)">
          <NexusText variant="h3">Tier Comparison & Lifecycle Management</NexusText>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { id: 'STARTER' as const, name: 'Café Starter', price: '$49/mo', desc: 'Single counter POS, basic shift register, up to 3 staff members.', active: false },
              { id: 'PRO' as const, name: 'Artisan Pro', price: '$149/mo', desc: 'Up to 10 POS stations, KDS Barista Canvas, Recipe BOM, Multi-tender.', active: true },
              { id: 'ENTERPRISE' as const, name: 'Roastery Enterprise', price: '$499/mo', desc: 'Multi-branch regional RLS, 24/7 dedicated support, custom tax slabs.', active: false },
            ].map((tier) => (
              <div
                key={tier.id}
                className={`p-4 rounded-xl border flex flex-col justify-between ${
                  tier.active
                    ? 'bg-primary/10 border-primary shadow-sm'
                    : 'bg-surface-container border-surface-container-highest'
                }`}
              >
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-bold text-sm text-on-surface">{tier.name}</span>
                    {tier.active && <NexusBadge variant="success" label="CURRENT" />}
                  </div>
                  <span className="font-mono text-xl font-bold text-primary block">{tier.price}</span>
                  <p className="text-xs text-outline mt-2">{tier.desc}</p>
                </div>
                <div className="mt-4 pt-3 border-t border-surface-container-highest">
                  <NexusButton
                    variant={tier.active ? 'outline' : 'primary'}
                    size="sm"
                    className="w-full justify-center text-xs"
                    onClick={() => setSelectedPlan(tier.id)}
                  >
                    {tier.active ? 'Manage Plan' : 'Upgrade &rarr;'}
                  </NexusButton>
                </div>
              </div>
            ))}
          </div>
        </NexusStack>
      </NexusCard>

      {/* Past Invoices Table */}
      <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
        <NexusStack gap="var(--nx-space-3)">
          <NexusText variant="h3">Audited Invoices & WORM Statements</NexusText>
          <div className="overflow-x-auto">
            <table className="nx-data-table">
              <thead>
                <tr className="border-b border-surface-container-highest text-outline">
                  <th className="py-2 px-3">Invoice Number</th>
                  <th className="py-2 px-3">Date</th>
                  <th className="py-2 px-3">Amount</th>
                  <th className="py-2 px-3">Card</th>
                  <th className="py-2 px-3">SHA-256 Digest</th>
                  <th className="py-2 px-3 text-right">Receipt</th>
                </tr>
              </thead>
              <tbody>
                {pastInvoices.map((inv) => (
                  <tr key={inv.id} className="border-b border-surface-container-highest/60 text-on-surface">
                    <td className="py-2.5 px-3 font-bold">{inv.id}</td>
                    <td className="py-2.5 px-3 text-outline">{inv.date}</td>
                    <td className="py-2.5 px-3 text-emerald-400 font-bold">{inv.amount}</td>
                    <td className="py-2.5 px-3 text-outline">{inv.card}</td>
                    <td className="py-2.5 px-3 text-outline text-[11px]">{inv.hash}</td>
                    <td className="py-2.5 px-3 text-right">
                      <NexusButton variant="outline" size="sm" onClick={() => setStatusNotice(`Preparing WORM PDF invoice download for ${inv.id}…`)}>
                        <NexusText variant="caption">Download PDF</NexusText>
                      </NexusButton>
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
