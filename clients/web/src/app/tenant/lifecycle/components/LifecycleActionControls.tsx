'use client';

import React from 'react';
import { NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { TenantStatus } from '../types';

export interface LifecycleActionControlsProps {
  readonly currentStatus: TenantStatus;
  readonly onTransition: (action: string) => void;
  readonly isBusy: boolean;
}

export function LifecycleActionControls({
  currentStatus,
  onTransition,
  isBusy,
}: LifecycleActionControlsProps): React.JSX.Element {
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
        <div>
          <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>
            Operational State Machine Transitions
          </NexusText>
          <NexusText variant="caption" role="muted">
            Gracefully shift workspace operational states across maintenance windows and emergency audits.
          </NexusText>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
          {currentStatus === 'ACTIVE' ? (
            <>
              <NexusButton
                variant="secondary"
                disabled={isBusy}
                onClick={() => onTransition('ENTER_MAINTENANCE')}
              >
                Enter Maintenance Mode
              </NexusButton>

              <NexusButton
                variant="secondary"
                disabled={isBusy}
                onClick={() => onTransition('DRAIN_TRANSACTIONS')}
              >
                Drain Active Folios
              </NexusButton>

              <NexusButton
                variant="destructive"
                disabled={isBusy}
                onClick={() => onTransition('SUSPEND')}
              >
                Suspend Workspace Lock
              </NexusButton>
            </>
          ) : (
            <NexusButton
              variant="primary"
              disabled={isBusy}
              onClick={() => onTransition('RESUME_ACTIVE')}
            >
              Resume Active Production Operations
            </NexusButton>
          )}
        </div>
      </NexusStack>
    </NexusBox>
  );
}
