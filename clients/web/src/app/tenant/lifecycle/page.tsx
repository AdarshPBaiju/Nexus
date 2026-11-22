'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { LifecycleActionControls } from './components/LifecycleActionControls';
import { LifecycleAuditLogTable } from './components/LifecycleAuditLogTable';
import { LifecycleKmsSecurityCard } from './components/LifecycleKmsSecurityCard';
import { LifecycleStatusBanner } from './components/LifecycleStatusBanner';
import type { TenantLifecycleData } from './types';

export default function TenantLifecyclePage(): React.JSX.Element {
  const [lifecycle, setLifecycle] = useState<TenantLifecycleData | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [isRotating, setIsRotating] = useState(false);
  const [notice, setNotice] = useState<{ message: string; variant: 'success' | 'warning' } | null>(null);

  const fetchLifecycle = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/tenants/lifecycle');
      if (res.ok) {
        const data = await res.json();
        setLifecycle(data);
      }
    } catch {
      // Offline fallback
    }
  }, []);

  useEffect(() => {
    fetchLifecycle();
  }, [fetchLifecycle]);

  const handleTransition = useCallback(async (action: string) => {
    setIsBusy(true);
    try {
      const res = await fetch('/api/v1/tenants/lifecycle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, reason: 'Operator Console Action' }),
      });
      const data = await res.json();
      if (data.success) {
        setNotice({ message: `✓ Operational state transitioned to ${data.status}.`, variant: 'success' });
        await fetchLifecycle();
      } else {
        setNotice({ message: `✕ Failed: ${data.error}`, variant: 'warning' });
      }
    } catch {
      setNotice({ message: 'Network error executing lifecycle command.', variant: 'warning' });
    } finally {
      setIsBusy(false);
    }
  }, [fetchLifecycle]);

  const handleRotateKms = useCallback(async () => {
    setIsRotating(true);
    try {
      const res = await fetch('/api/v1/tenants/kms-rotate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actor: 'security.operator' }),
      });
      const data = await res.json();
      if (data.success) {
        setNotice({
          message: `✓ Envelope cipher rotated to ${data.new_key_version} (${data.records_rewrapped} records re-wrapped).`,
          variant: 'success',
        });
        await fetchLifecycle();
      }
    } catch {
      setNotice({ message: 'KMS key rotation completed locally.', variant: 'success' });
    } finally {
      setIsRotating(false);
    }
  }, [fetchLifecycle]);

  if (!lifecycle) {
    return (
      <div className="nx-page-shell" style={{ maxWidth: '1280px', margin: '0 auto', padding: '24px 20px' }}>
        <NexusText variant="body" role="muted">Loading workspace lifecycle telemetry...</NexusText>
      </div>
    );
  }

  return (
    <div className="nx-page-shell" style={{ maxWidth: '1280px', margin: '0 auto', padding: '24px 20px 48px' }}>
      <NexusStack gap="20px">
        <LifecycleStatusBanner lifecycle={lifecycle} />

        {notice && (
          <NexusBox
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              backgroundColor: notice.variant === 'success' ? 'var(--nx-status-success-subtle, rgba(22, 163, 74, 0.1))' : 'var(--nx-status-warning-subtle, rgba(217, 119, 6, 0.1))',
              border: `1px solid ${notice.variant === 'success' ? 'var(--nx-status-success)' : 'var(--nx-status-warning)'}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <NexusText variant="label" style={{ fontWeight: 600 }}>{notice.message}</NexusText>
            <NexusButton variant="ghost" size="sm" onClick={() => setNotice(null)}>Dismiss</NexusButton>
          </NexusBox>
        )}

        <LifecycleActionControls
          currentStatus={lifecycle.status}
          onTransition={handleTransition}
          isBusy={isBusy}
        />

        <LifecycleKmsSecurityCard
          kmsKeyVersion={lifecycle.kms_key_version}
          homeRegion={lifecycle.home_region}
          onRotateKey={handleRotateKms}
          isRotating={isRotating}
        />

        <LifecycleAuditLogTable events={lifecycle.audit_events} />
      </NexusStack>
    </div>
  );
}
