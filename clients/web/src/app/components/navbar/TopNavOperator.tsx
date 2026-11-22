'use client';

import React from 'react';
import { NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { StaffProfile } from '../../../runtime/auth/AuthContext';

export interface TopNavOperatorProps {
  readonly session: { readonly name: string; readonly role: string; readonly workstationId: string };
  readonly activeStaff: StaffProfile;
  readonly onLock: () => void;
}

export function TopNavOperator({ session, activeStaff, onLock }: TopNavOperatorProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '9px',
        paddingInlineStart: '9px',
        borderInlineStart: '1px solid var(--nx-border-subtle)',
      }}
    >
      <span
        aria-hidden="true"
        style={{
          width: '26px',
          height: '26px',
          borderRadius: '9999px',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'var(--nx-surface-subtle)',
          border: '1px solid var(--nx-border-default)',
          fontSize: '13px',
        }}
      >
        {activeStaff.avatarIcon}
      </span>
      <NexusStack gap="0px">
        <NexusText variant="label" style={{ lineHeight: '15px' }}>
          {session.name}
        </NexusText>
        <NexusText variant="caption" role="muted" style={{ fontSize: '10px', lineHeight: '13px' }}>
          {session.role} · {session.workstationId}
        </NexusText>
      </NexusStack>
      <NexusButton
        variant="ghost"
        size="sm"
        onClick={onLock}
        title="Lock workstation — PIN required to resume"
        ariaLabel="Lock workstation"
      >
        <span className="material-symbols-outlined" style={{ fontSize: '16px' }} aria-hidden="true">
          lock
        </span>
      </NexusButton>
    </NexusBox>
  );
}
