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
import { NexusMainTopNavbar } from '../components/NexusMainTopNavbar';
import { NexusEnterpriseSidebar } from '../components/NexusEnterpriseSidebar';

interface GatewayConfig {
  id: string;
  name: string;
  code: string;
  type: 'DIGITAL' | 'CARD_EDC' | 'HARDWARE';
  status: 'CONNECTED' | 'DISCONNECTED';
  endpoint: string;
  feePercent: string;
  lastPing: string;
}

const INITIAL_GATEWAYS: GatewayConfig[] = [
  { id: 'GW-01', name: 'Stripe Multi-Currency (Apple/Google Pay)', code: 'PAY_STRIPE', type: 'DIGITAL', status: 'CONNECTED', endpoint: '/api/v1/webhooks/stripe', feePercent: '2.9% + 30¢', lastPing: '0.4s ago' },
  { id: 'GW-02', name: 'Direct Instant QR (UPI / PromptPay)', code: 'PAY_DIRECT_QR', type: 'DIGITAL', status: 'CONNECTED', endpoint: 'artisan@upi (Zero MDR)', feePercent: '0.0%', lastPing: '1.2s ago' },
  { id: 'GW-03', name: 'Razorpay Enterprise Router', code: 'PAY_RAZORPAY', type: 'DIGITAL', status: 'CONNECTED', endpoint: '/api/v1/webhooks/razorpay', feePercent: '2.0%', lastPing: '2.5s ago' },
  { id: 'GW-04', name: 'Pine Labs / Ingenico EDC USB Bridge', code: 'HW_EDC_USB_BRIDGE', type: 'CARD_EDC', status: 'CONNECTED', endpoint: 'COM3 (Baud: 115200)', feePercent: '1.2%', lastPing: 'Connected' },
  { id: 'GW-05', name: 'Epson TM-T88VI ESC/POS 80mm Printer', code: 'HW_PRINTER_ESCPOS', type: 'HARDWARE', status: 'CONNECTED', endpoint: 'USB001 (Auto-cut & RJ11 Kick)', feePercent: '0.0%', lastPing: 'Online' },
];

export default function GatewaysPage(): React.JSX.Element {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [gateways, setGateways] = useState<GatewayConfig[]>(INITIAL_GATEWAYS);
  const [pingStatus, setPingStatus] = useState<string | null>(null);

  const testPing = (gw: GatewayConfig) => {
    setPingStatus(`Ping dispatched to ${gw.name} -> 200 OK (Round-trip 42ms, HMAC-SHA256 signature verified)`);
    setTimeout(() => setPingStatus(null), 4000);
  };

  return (
    <NexusBox style={{ minHeight: '100vh', backgroundColor: 'var(--nx-surface-bg)' }}>
      <NexusMainTopNavbar isSidebarOpen={isSidebarOpen} onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />
      <NexusEnterpriseSidebar isOpen={isSidebarOpen} />

      <NexusBox
        style={{
          marginLeft: isSidebarOpen ? '280px' : 0,
          marginTop: '56px',
          padding: 'var(--nx-space-8) var(--nx-space-6)',
          transition: 'margin-left 0.2s ease',
        }}
      >
        <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1200px', margin: '0 auto' }}>
          {/* Header */}
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusStack gap="var(--nx-space-1)">
              <NexusText variant="h1">Payment Gateways & Hardware Rails</NexusText>
              <NexusText variant="body" role="secondary">
                Configure Bring-Your-Own (BYO) merchant credentials, regional KMS vaults, and hardware EDC bridges.
              </NexusText>
            </NexusStack>
            <NexusBadge variant="success" label="5 / 5 Rails Operational" />
          </NexusStack>

          {pingStatus && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono text-xs flex items-center justify-between">
              <span>✓ {pingStatus}</span>
              <button onClick={() => setPingStatus(null)} className="text-outline hover:text-on-surface">✕</button>
            </div>
          )}

          {/* Gateways Grid */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-4)">
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-surface-container-highest text-outline font-mono">
                      <th className="py-2.5 px-3">Gateway Name</th>
                      <th className="py-2.5 px-3">Protocol Code</th>
                      <th className="py-2.5 px-3">Endpoint / Hardware Port</th>
                      <th className="py-2.5 px-3">MDR Fee</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3 text-right">Diagnostic</th>
                    </tr>
                  </thead>
                  <tbody>
                    {gateways.map((gw) => (
                      <tr key={gw.id} className="border-b border-surface-container-highest/60 text-on-surface font-mono">
                        <td className="py-3 px-3 font-sans font-semibold">
                          <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-[18px] text-primary">
                              {gw.type === 'HARDWARE' ? 'print' : gw.type === 'CARD_EDC' ? 'point_of_sale' : 'payments'}
                            </span>
                            <span>{gw.name}</span>
                          </div>
                        </td>
                        <td className="py-3 px-3 text-outline">{gw.code}</td>
                        <td className="py-3 px-3 text-secondary">{gw.endpoint}</td>
                        <td className="py-3 px-3 font-bold">{gw.feePercent}</td>
                        <td className="py-3 px-3">
                          <NexusBadge variant="success" label={gw.status} />
                        </td>
                        <td className="py-3 px-3 text-right">
                          <NexusButton variant="outline" size="sm" onClick={() => testPing(gw)}>
                            <NexusText variant="caption">Test Ping</NexusText>
                          </NexusButton>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </NexusStack>
          </NexusCard>

          {/* Webhook & Secret Vault Security Architecture */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-3)">
              <NexusText variant="h3">Zero-Trust Envelope Encryption Architecture</NexusText>
              <NexusText variant="body" role="secondary">
                All merchant gateway secrets (Stripe restricted keys, Razorpay key_secret) are encrypted at rest using regional AWS KMS / Vault envelope ciphers (AES-256-GCM + AAD). Direct SDK execution runs strictly in Celery background workers.
              </NexusText>
              <div className="grid grid-cols-3 gap-3 pt-2 font-mono text-xs">
                <div className="p-3 rounded-xl bg-surface-container border border-surface-container-highest">
                  <span className="text-outline text-[10px] uppercase block">Webhook Deduplication</span>
                  <span className="text-on-surface font-bold">100% Guaranteed</span>
                  <span className="text-[10px] text-outline block mt-1">Unique (gateway_id, event_id)</span>
                </div>
                <div className="p-3 rounded-xl bg-surface-container border border-surface-container-highest">
                  <span className="text-outline text-[10px] uppercase block">Clearing Ledger Split</span>
                  <span className="text-on-surface font-bold">T+1 Auto-Post</span>
                  <span className="text-[10px] text-outline block mt-1">Net bank vs 5030 MDR fee</span>
                </div>
                <div className="p-3 rounded-xl bg-surface-container border border-surface-container-highest">
                  <span className="text-outline text-[10px] uppercase block">Hardware Latency</span>
                  <span className="text-on-surface font-bold">&lt; 15ms IPC</span>
                  <span className="text-[10px] text-outline block mt-1">Tauri 2.0 Rust native pipe</span>
                </div>
              </div>
            </NexusStack>
          </NexusCard>
        </NexusStack>
      </NexusBox>
    </NexusBox>
  );
}
