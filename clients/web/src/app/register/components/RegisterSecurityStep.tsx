'use client';

import React from 'react';
import { NexusBox, NexusPinInput, NexusStack, NexusText, NexusTextInput } from '@nexus/ui';

export interface RegisterSecurityData {
  admin_email: string;
  master_pin: string;
  kms_alias: string;
}

export interface RegisterSecurityStepProps {
  readonly data: RegisterSecurityData;
  readonly onChange: (updated: Partial<RegisterSecurityData>) => void;
}

export function RegisterSecurityStep({ data, onChange }: RegisterSecurityStepProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '24px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="18px">
        <div>
          <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
            Security, Superadmin & Encryption
          </NexusText>
          <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
            Configure root owner authentication, offline cashier override PIN, and zero-trust envelope keys.
          </NexusText>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NexusTextInput
            labelKey="Owner / Superadmin Email"
            value={data.admin_email}
            onChange={(val: string) => onChange({ admin_email: val })}
            placeholderKey="founder@nexus-cafe.io"
          />

          <NexusTextInput
            labelKey="Regional KMS Key Alias"
            value={data.kms_alias}
            onChange={(val: string) => onChange({ kms_alias: val })}
            placeholderKey="alias/nexus-aes256gcm-tenant-key"
          />
        </div>

        <div style={{ maxWidth: '320px', paddingTop: '6px' }}>
          <NexusPinInput
            labelKey="Master Cashier Security PIN (4-Digits)"
            length={4}
            value={data.master_pin}
            onChange={(val: string) => onChange({ master_pin: val })}
          />
          <NexusText variant="caption" role="muted" style={{ marginTop: '4px' }}>
            Used for emergency cashier register unlock, blind count closes, and refund authorization.
          </NexusText>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
