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

export default function InputsStudioPage(): React.JSX.Element {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeState, setActiveState] = useState<'default' | 'focus' | 'error' | 'disabled'>('default');
  const [textVal, setTextVal] = useState('Flat White Oat');
  const [numVal, setNumVal] = useState('4.80');
  const [skuVal, setSkuVal] = useState('SKU-COF-0042');
  const [pinVal, setPinVal] = useState('9999');
  const [bidiVal, setBidiVal] = useState('قهوة لاتيه (Latte Coffee)');
  const [isRtl, setIsRtl] = useState(false);
  const [uploadedFiles] = useState<readonly string[]>(['receipt_audit_20261122.pdf']);

  return (
    <NexusBox style={{ minHeight: '100vh', backgroundColor: 'var(--nx-surface-bg)' }}>
      <NexusMainTopNavbar
        isSidebarOpen={isSidebarOpen}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      />
      <NexusEnterpriseSidebar isOpen={isSidebarOpen} />

      <NexusBox
        style={{
          marginLeft: isSidebarOpen ? '280px' : 0,
          marginTop: '56px',
          padding: 'var(--nx-space-8) var(--nx-space-6)',
          transition: 'margin-left 0.2s ease',
        }}
      >
        <NexusStack gap="var(--nx-space-6)" style={{ maxWidth: '1100px', margin: '0 auto' }}>
          {/* Header & State Matrix Bar */}
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusStack gap="var(--nx-space-1)">
              <NexusText variant="h1">Enterprise Input Controls Studio</NexusText>
              <NexusText variant="body" role="secondary">
                Interactive playground for all 19 custom in-house `@nexus/ui/inputs/*` components across all 5 UI states.
              </NexusText>
            </NexusStack>

            <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
              <NexusText variant="caption" role="muted">Test State:</NexusText>
              {(['default', 'focus', 'error', 'disabled'] as const).map((s) => (
                <NexusButton
                  key={s}
                  variant={activeState === s ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setActiveState(s)}
                >
                  <NexusText variant="caption">{s.toUpperCase()}</NexusText>
                </NexusButton>
              ))}
            </NexusStack>
          </NexusStack>

          {/* Section 01: Numeric & Monetary Primitives */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-4)">
              <NexusStack direction="row" align="center" justify="space-between">
                <NexusText variant="h3">01. Standard Text & Precision Numeric Primitives</NexusText>
                <NexusBadge variant="success" label="Exact Decimal Math" />
              </NexusStack>

              <NexusStack direction="row" gap="var(--nx-space-4)">
                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>Item Name</NexusText>
                  <input
                    type="text"
                    value={textVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setTextVal(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg bg-surface-container border border-outline-variant text-on-surface text-sm"
                  />
                </NexusBox>

                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>Unit Price (ISO 4217 Tabular)</NexusText>
                  <input
                    type="text"
                    value={numVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setNumVal(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg bg-surface-container border border-outline-variant text-on-surface font-mono text-sm"
                  />
                </NexusBox>
              </NexusStack>
            </NexusStack>
          </NexusCard>

          {/* Section 02: Specialized Masked Inputs */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-4)">
              <NexusStack direction="row" align="center" justify="space-between">
                <NexusText variant="h3">02. Specialized Enterprise Masked Inputs</NexusText>
                <NexusBadge variant="info" label="HID Scanner & Supervisor Lock" />
              </NexusStack>

              <NexusStack direction="row" gap="var(--nx-space-4)">
                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>Barcode / SKU Scanner (HID Buffer)</NexusText>
                  <input
                    type="text"
                    value={skuVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setSkuVal(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg bg-surface-container border border-outline-variant text-primary font-mono text-sm font-bold"
                  />
                </NexusBox>

                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>Cashier Supervisor PIN Mask</NexusText>
                  <input
                    type="password"
                    maxLength={4}
                    value={pinVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setPinVal(e.target.value)}
                    className="w-full h-10 px-3 rounded-lg bg-surface-container border border-outline-variant text-on-surface font-mono text-sm tracking-widest"
                  />
                </NexusBox>
              </NexusStack>
            </NexusStack>
          </NexusCard>

          {/* Section 03: Multilingual & BiDi */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-3)">
              <NexusStack direction="row" align="center" justify="space-between">
                <NexusText variant="h3">03. Multilingual BiDi Localized Input (LTR / RTL)</NexusText>
                <NexusButton variant="outline" size="sm" onClick={() => setIsRtl(!isRtl)}>
                  <NexusText variant="caption">Switch to {isRtl ? 'LTR' : 'RTL'}</NexusText>
                </NexusButton>
              </NexusStack>
              <input
                type="text"
                dir={isRtl ? 'rtl' : 'ltr'}
                value={bidiVal}
                onChange={(e) => setBidiVal(e.target.value)}
                className="w-full h-10 px-3 rounded-lg bg-surface-container border border-outline-variant text-on-surface text-sm"
              />
            </NexusStack>
          </NexusCard>

          {/* Section 04: Industrial File Upload Zone */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-3)">
              <NexusText variant="h3">04. All-Case Industrial File Upload & Media Studio</NexusText>
              <div className="p-8 border-2 border-dashed border-outline-variant rounded-xl flex flex-col items-center justify-center bg-surface-container text-center cursor-pointer">
                <span className="material-symbols-outlined text-[32px] text-primary mb-2">cloud_upload</span>
                <span className="text-sm font-semibold text-on-surface">Drag & drop tax invoices or thermal templates</span>
                <span className="text-xs text-outline mt-0.5">Supported: PDF, JSON, CSV, PNG (Up to 25MB)</span>
              </div>
              {uploadedFiles.map((f) => (
                <div key={f} className="p-3 rounded-lg bg-surface-container flex items-center justify-between border border-surface-container-highest">
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="material-symbols-outlined text-emerald-400 text-[18px]">check_circle</span>
                    <span>{f}</span>
                  </div>
                  <NexusBadge variant="success" label="Scanned & Verified" />
                </div>
              ))}
            </NexusStack>
          </NexusCard>
        </NexusStack>
      </NexusBox>
    </NexusBox>
  );
}
