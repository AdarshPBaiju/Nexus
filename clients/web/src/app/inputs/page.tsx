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
  const [uploadedFiles, setUploadedFiles] = useState<readonly string[]>(['receipt_audit_20261122.pdf']);

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

          {/* Section 01: Precision Numeric & Monetary Primitives */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-4)">
              <NexusStack direction="row" align="center" justify="space-between">
                <NexusText variant="h3">01. Standard Text & Precision Numeric Primitives</NexusText>
                <NexusBadge variant="success" label="Exact Decimal Math" />
              </NexusStack>

              <NexusStack direction="row" gap="var(--nx-space-4)">
                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>
                    Item Display Name
                  </NexusText>
                  <input
                    type="text"
                    value={textVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setTextVal(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--nx-surface-subtle)',
                      border: activeState === 'error' ? '1px solid var(--nx-status-danger)' : '1px solid var(--nx-border-default)',
                      color: 'var(--nx-text-primary)',
                      fontFamily: 'inherit',
                      fontSize: '14px',
                    }}
                  />
                </NexusBox>

                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>
                    Unit Price (ISO 4217 Tabular Numerals)
                  </NexusText>
                  <NexusBox style={{ position: 'relative' }}>
                    <span style={{ position: 'absolute', left: '10px', top: '8px', color: 'var(--nx-text-muted)' }}>$</span>
                    <input
                      type="text"
                      value={numVal}
                      disabled={activeState === 'disabled'}
                      onChange={(e) => setNumVal(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '8px 12px 8px 24px',
                        borderRadius: '6px',
                        backgroundColor: 'var(--nx-surface-subtle)',
                        border: activeState === 'error' ? '1px solid var(--nx-status-danger)' : '1px solid var(--nx-border-default)',
                        color: 'var(--nx-text-primary)',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '14px',
                      }}
                    />
                  </NexusBox>
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
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>
                    Barcode / SKU Scanner (HID Buffer)
                  </NexusText>
                  <input
                    type="text"
                    value={skuVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setSkuVal(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--nx-surface-subtle)',
                      border: '1px solid var(--nx-border-default)',
                      color: 'var(--nx-action-primary)',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '14px',
                      fontWeight: 600,
                    }}
                  />
                </NexusBox>

                <NexusBox style={{ flex: 1 }}>
                  <NexusText variant="label" style={{ marginBottom: '6px', display: 'block' }}>
                    Cashier Supervisor PIN Mask
                  </NexusText>
                  <input
                    type="password"
                    maxLength={4}
                    value={pinVal}
                    disabled={activeState === 'disabled'}
                    onChange={(e) => setPinVal(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      backgroundColor: 'var(--nx-surface-subtle)',
                      border: '1px solid var(--nx-border-default)',
                      color: 'var(--nx-text-primary)',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '14px',
                      letterSpacing: '0.3em',
                    }}
                  />
                </NexusBox>
              </NexusStack>
            </NexusStack>
          </NexusCard>

          {/* Section 03: Multilingual & BiDi */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-4)">
              <NexusStack direction="row" align="center" justify="space-between">
                <NexusText variant="h3">03. Multilingual BiDi Localized Input (LTR / RTL)</NexusText>
                <NexusButton variant="outline" size="sm" onClick={() => setIsRtl(!isRtl)}>
                  <NexusText variant="caption">Switch to {isRtl ? 'LTR' : 'RTL'}</NexusText>
                </NexusButton>
              </NexusStack>

              <NexusBox>
                <input
                  type="text"
                  dir={isRtl ? 'rtl' : 'ltr'}
                  value={bidiVal}
                  onChange={(e) => setBidiVal(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    borderRadius: '6px',
                    backgroundColor: 'var(--nx-surface-subtle)',
                    border: '1px solid var(--nx-border-default)',
                    color: 'var(--nx-text-primary)',
                    fontFamily: 'inherit',
                    fontSize: '14px',
                    direction: isRtl ? 'rtl' : 'ltr',
                  }}
                />
              </NexusBox>
            </NexusStack>
          </NexusCard>

          {/* Section 04: Industrial File Upload Zone */}
          <NexusCard elevation="card" style={{ padding: 'var(--nx-space-5)' }}>
            <NexusStack gap="var(--nx-space-3)">
              <NexusText variant="h3">04. All-Case Industrial File Upload & Media Studio</NexusText>
              <NexusBox
                padding="var(--nx-space-8)"
                style={{
                  border: '2px dashed var(--nx-border-default)',
                  borderRadius: '8px',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'var(--nx-surface-subtle)',
                  cursor: 'pointer',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: '32px', color: 'var(--nx-action-primary)', marginBottom: '8px' }}>
                  cloud_upload
                </span>
                <NexusText variant="label">Drag & drop tax invoices, thermal print templates, or bulk catalogs</NexusText>
                <NexusText variant="caption" role="muted">Supported: PDF, JSON, CSV, PNG (Up to 25MB)</NexusText>
              </NexusBox>

              {uploadedFiles.map((f) => (
                <NexusBox
                  key={f}
                  padding="8px 12px"
                  style={{
                    backgroundColor: 'var(--nx-surface-subtle)',
                    borderRadius: '6px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
                    <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--nx-status-success)' }}>
                      check_circle
                    </span>
                    <NexusText variant="caption" tabular>{f}</NexusText>
                  </NexusStack>
                  <NexusBadge variant="success" label="Scanned & Verified" />
                </NexusBox>
              ))}
            </NexusStack>
          </NexusCard>
        </NexusStack>
      </NexusBox>
    </NexusBox>
  );
}
