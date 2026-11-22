'use client';

import React from 'react';
import { NexusBox, NexusButton, NexusStack, NexusSwitch, NexusText, NexusTextInput } from '@nexus/ui';

export interface RazorpayConfigData {
  enabled: boolean;
  mode: string;
  key_id: string;
  key_secret_masked: string;
  webhook_secret_masked: string;
  auto_capture: boolean;
}

export interface GatewayRazorpayConfigProps {
  readonly config: RazorpayConfigData;
  readonly onChange: (updated: Partial<RazorpayConfigData>) => void;
  readonly onTest: () => void;
  readonly isTesting: boolean;
}

export function GatewayRazorpayConfig({
  config,
  onChange,
  onTest,
  isTesting,
}: GatewayRazorpayConfigProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '20px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="16px">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>
              Razorpay Enterprise Gateway
            </NexusText>
            <NexusText variant="caption" role="muted">
              UPI Intent, Indian Cards, Netbanking & EMI Router
            </NexusText>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <NexusSwitch
              labelKey="Enable Razorpay Rail"
              value={config.enabled}
              onChange={(val: boolean) => onChange({ enabled: val })}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
          <NexusTextInput
            labelKey="Razorpay Key ID"
            value={config.key_id}
            onChange={(val: string) => onChange({ key_id: val })}
            placeholderKey="rzp_live_... or rzp_test_..."
          />
          <NexusTextInput
            labelKey="Key Secret (AES-256 Encrypted)"
            value={config.key_secret_masked}
            onChange={(val: string) => onChange({ key_secret_masked: val })}
            placeholderKey="••••••••••••••••••••"
          />
          <NexusTextInput
            labelKey="Webhook Signing Secret"
            value={config.webhook_secret_masked}
            onChange={(val: string) => onChange({ webhook_secret_masked: val })}
            placeholderKey="Secret string configured in Razorpay dashboard"
          />
          <div style={{ display: 'flex', alignItems: 'center', paddingTop: '22px' }}>
            <NexusSwitch
              labelKey="Auto-Capture Authorized Transactions"
              value={config.auto_capture}
              onChange={(val: boolean) => onChange({ auto_capture: val })}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--nx-border-subtle)' }}>
          <NexusButton
            variant="secondary"
            size="sm"
            disabled={isTesting || !config.enabled}
            onClick={onTest}
          >
            {isTesting ? 'Testing Handshake...' : 'Test Razorpay API Ping'}
          </NexusButton>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
