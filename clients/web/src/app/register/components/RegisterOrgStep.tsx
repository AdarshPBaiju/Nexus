'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusSelect, NexusStack, NexusText, NexusTextInput } from '@nexus/ui';

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

  const cloudSubdomain = `${data.slug || 'your-cafe'}.nexus-qsr.io`;

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
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
              Cloud Organization & Regional Cell
            </NexusText>
            <NexusBadge variant="success" label="CLOUD SAAS MESH" />
          </NexusStack>
          <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
            Configure your enterprise tenant partition on the multi-region cloud mesh with Forced RLS isolation.
          </NexusText>
        </div>

        {/* Live Cloud Subdomain Preview Banner */}
        <NexusBox
          style={{
            padding: '12px 14px',
            borderRadius: '8px',
            backgroundColor: 'var(--nx-surface-subtle)',
            border: '1px solid var(--nx-border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div>
            <NexusText variant="caption" role="muted" style={{ display: 'block' }}>
              PROVISIONED CLOUD SAAS URL
            </NexusText>
            <NexusText variant="label" style={{ fontFamily: 'var(--font-mono, monospace)', fontWeight: 600, color: 'var(--nx-action-primary)' }}>
              https://{cloudSubdomain}
            </NexusText>
          </div>
          <NexusBadge variant="neutral" label="FORCED RLS CELL" />
        </NexusBox>

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
