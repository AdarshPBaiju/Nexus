'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';

export interface LifecycleKmsSecurityCardProps {
  readonly kmsKeyVersion: string;
  readonly homeRegion: string;
  readonly onRotateKey: () => void;
  readonly isRotating: boolean;
}

export function LifecycleKmsSecurityCard({
  kmsKeyVersion,
  homeRegion,
  onRotateKey,
  isRotating,
}: LifecycleKmsSecurityCardProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '20px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="14px">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>
              Zero-Trust Envelope Encryption & Regional KMS
            </NexusText>
            <NexusText variant="caption" role="muted">
              AES-256-GCM authenticated envelope cipher with tenant-bound Additional Authenticated Data (AAD)
            </NexusText>
          </div>
          <NexusBadge variant="success" label="Active Sovereign Cipher" />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px' }}>
          <NexusBox
            style={{
              padding: '12px',
              borderRadius: '8px',
              backgroundColor: 'var(--nx-surface-subtle)',
              border: '1px solid var(--nx-border-subtle)',
            }}
          >
            <NexusText variant="caption" role="muted">ACTIVE ENVELOPE KEY VERSION</NexusText>
            <NexusText variant="code" style={{ fontWeight: 700, marginTop: '2px' }}>{kmsKeyVersion}</NexusText>
          </NexusBox>

          <NexusBox
            style={{
              padding: '12px',
              borderRadius: '8px',
              backgroundColor: 'var(--nx-surface-subtle)',
              border: '1px solid var(--nx-border-subtle)',
            }}
          >
            <NexusText variant="caption" role="muted">HARDWARE SECURITY MODULE (HSM)</NexusText>
            <NexusText variant="body" style={{ fontWeight: 600, marginTop: '2px' }}>FIPS 140-3 Level 3 ({homeRegion})</NexusText>
          </NexusBox>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '8px' }}>
          <NexusButton
            variant="secondary"
            size="sm"
            disabled={isRotating}
            onClick={onRotateKey}
          >
            {isRotating ? 'Rotating Envelope Cipher...' : 'Rotate KMS Envelope Key Now'}
          </NexusButton>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
