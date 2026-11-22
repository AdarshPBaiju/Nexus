'use client';

import React from 'react';
import { NexusBox, NexusSelect, NexusStack, NexusText, NexusTextInput } from '@nexus/ui';

export interface RegisterOrgData {
  legal_name: string;
  slug: string;
  home_region: string;
  tax_identifier: string;
}

export interface RegisterOrgStepProps {
  readonly data: RegisterOrgData;
  readonly onChange: (updated: Partial<RegisterOrgData>) => void;
}

export function RegisterOrgStep({ data, onChange }: RegisterOrgStepProps): React.JSX.Element {
  const handleNameChange = (name: string) => {
    const slug = name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)+/g, '');
    onChange({ legal_name: name, slug });
  };

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
            Organization & Regional Residency
          </NexusText>
          <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
            Set your registered business entity and sovereign cloud data residency region.
          </NexusText>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <NexusTextInput
            labelKey="Legal Entity Name"
            value={data.legal_name}
            onChange={handleNameChange}
            placeholderKey="e.g. Nexus Roasters & Café Pvt Ltd"
          />

          <NexusTextInput
            labelKey="Tenant Workspace Slug"
            value={data.slug}
            onChange={(val: string) => onChange({ slug: val })}
            placeholderKey="nexus-roasters-cafe"
          />

          <NexusSelect
            labelKey="Sovereign Cloud Data Residency Region"
            value={data.home_region}
            onChange={(val: string) => onChange({ home_region: val })}
            options={[
              { value: 'ap-south-1', label: 'Asia Pacific (Mumbai, India) — ap-south-1' },
              { value: 'us-east-1', label: 'US East (N. Virginia, USA) — us-east-1' },
              { value: 'eu-west-1', label: 'Europe (Dublin, Ireland) — eu-west-1' },
              { value: 'me-central-1', label: 'Middle East (UAE) — me-central-1' },
            ]}
          />

          <NexusTextInput
            labelKey="Statutory Tax ID / GSTIN"
            value={data.tax_identifier}
            onChange={(val: string) => onChange({ tax_identifier: val })}
            placeholderKey="e.g. 29AAAAA0000A1Z5"
          />
        </div>
      </NexusStack>
    </NexusBox>
  );
}
