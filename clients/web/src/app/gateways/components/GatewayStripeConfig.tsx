'use client';

import React from 'react';
import { NexusBox, NexusButton, NexusStack, NexusSwitch, NexusText, NexusTextInput } from '@nexus/ui';

export interface StripeConfigData {
  enabled: boolean;
  mode: string;
  publishable_key: string;
  secret_key_masked: string;
  webhook_secret_masked: string;
  webhook_url: string;
  three_d_secure: string;
}

export interface GatewayStripeConfigProps {
  readonly config: StripeConfigData;
  readonly onChange: (updated: Partial<StripeConfigData>) => void;
  readonly onTest: () => void;
  readonly isTesting: boolean;
}

export function GatewayStripeConfig({
  config,
  onChange,
  onTest,
  isTesting,
}: GatewayStripeConfigProps): React.JSX.Element {
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
              Stripe Multi-Rail Payments
            </NexusText>
            <NexusText variant="caption" role="muted">
              Credit Cards, Apple Pay, Google Pay & Regional Wallets (PCI-DSS 4.0 SAQ-A)
            </NexusText>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <NexusSwitch
              labelKey="Enable Stripe Rail"
              value={config.enabled}
              onChange={(val: boolean) => onChange({ enabled: val })}
            />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
          <NexusTextInput
            labelKey="Stripe Publishable Key"
            value={config.publishable_key}
            onChange={(val: string) => onChange({ publishable_key: val })}
            placeholderKey="pk_live_... or pk_test_..."
          />
          <NexusTextInput
            labelKey="Secret Key (Envelope Encrypted)"
            value={config.secret_key_masked}
            onChange={(val: string) => onChange({ secret_key_masked: val })}
            placeholderKey="sk_live_... or sk_test_..."
          />
          <NexusTextInput
            labelKey="Webhook Secret"
            value={config.webhook_secret_masked}
            onChange={(val: string) => onChange({ webhook_secret_masked: val })}
            placeholderKey="whsec_..."
          />
          <NexusTextInput
            labelKey="Inbound Webhook Endpoint"
            value={config.webhook_url}
            onChange={(val: string) => onChange({ webhook_url: val })}
            placeholderKey="https://api.yourdomain.com/webhooks/stripe"
            isDisabled
          />
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', paddingTop: '10px', borderTop: '1px solid var(--nx-border-subtle)' }}>
          <NexusButton
            variant="secondary"
            size="sm"
            disabled={isTesting || !config.enabled}
            onClick={onTest}
          >
            {isTesting ? 'Testing Handshake...' : 'Test Stripe API Ping'}
          </NexusButton>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
