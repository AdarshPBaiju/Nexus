'use client';

import React from 'react';
import { NexusBox, NexusSelect, NexusStack, NexusText, NexusTextInput } from '@nexus/ui';

export interface RegisterBranchData {
  branch_name: string;
  currency: string;
  timezone: string;
  terminal_id: string;
}

export interface RegisterBranchStepProps {
  readonly data: RegisterBranchData;
  readonly onChange: (updated: Partial<RegisterBranchData>) => void;
}

export function RegisterBranchStep({ data, onChange }: RegisterBranchStepProps): React.JSX.Element {
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
            Initial Branch & Currency Foundation
          </NexusText>
          <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
            Set up your venue's primary store, statutory currency, and first counter register.
          </NexusText>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NexusTextInput
            labelKey="Flagship Branch Name"
            value={data.branch_name}
            onChange={(val: string) => onChange({ branch_name: val })}
            placeholderKey="e.g. Flagship Café & Roastery - Indiranagar"
          />

          <NexusSelect
            labelKey="Base Accounting Currency"
            value={data.currency}
            onChange={(val: string) => onChange({ currency: val })}
            options={[
              { value: 'INR', label: 'INR (₹) — Indian Rupee' },
              { value: 'USD', label: 'USD ($) — United States Dollar' },
              { value: 'EUR', label: 'EUR (€) — Euro' },
              { value: 'AED', label: 'AED (د.إ) — UAE Dirham' },
              { value: 'GBP', label: 'GBP (£) — British Pound' },
            ]}
          />

          <NexusSelect
            labelKey="Store Operational Timezone"
            value={data.timezone}
            onChange={(val: string) => onChange({ timezone: val })}
            options={[
              { value: 'Asia/Kolkata', label: 'Asia/Kolkata (IST +05:30)' },
              { value: 'America/New_York', label: 'America/New_York (EST -05:00)' },
              { value: 'Europe/London', label: 'Europe/London (GMT +00:00)' },
              { value: 'Asia/Dubai', label: 'Asia/Dubai (GST +04:00)' },
            ]}
          />

          <NexusTextInput
            labelKey="First Register Terminal ID"
            value={data.terminal_id}
            onChange={(val: string) => onChange({ terminal_id: val })}
            placeholderKey="POS-COUNTER-01"
          />
        </div>
      </NexusStack>
    </NexusBox>
  );
}
