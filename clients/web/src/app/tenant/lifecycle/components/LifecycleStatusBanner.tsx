'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusStack, NexusText } from '@nexus/ui';
import type { TenantLifecycleData } from '../types';

export interface LifecycleStatusBannerProps {
  readonly lifecycle: TenantLifecycleData;
}

export function LifecycleStatusBanner({ lifecycle }: LifecycleStatusBannerProps): React.JSX.Element {
  const statusVariant = {
    ACTIVE: 'success' as const,
    MAINTENANCE: 'warning' as const,
    DRAINING: 'warning' as const,
    SUSPENDED: 'danger' as const,
  }[lifecycle.status];

  return (
    <NexusBox
      style={{
        padding: '20px 24px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="14px">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
                {lifecycle.legal_name}
              </NexusText>
              <NexusBadge variant={statusVariant} label={lifecycle.status} />
              <NexusBadge variant="info" label={lifecycle.home_region} />
            </div>
            <NexusText variant="code" role="muted" style={{ marginTop: '4px' }}>
              Tenant Root Slug: <strong>{lifecycle.slug}</strong> | Cell ID: {lifecycle.tenant_id.slice(0, 16)}...
            </NexusText>
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <NexusBadge variant="neutral" label={`${lifecycle.active_branches} Branches`} />
            <NexusBadge variant="neutral" label={`${lifecycle.active_stations} Stations`} />
            <NexusBadge variant="success" label={lifecycle.compliance_mode} />
            <NexusBadge variant="info" label={lifecycle.pci_dss_level} />
          </div>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
