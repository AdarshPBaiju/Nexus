'use client';

import React from 'react';
import { NexusText } from '@nexus/ui';
import type { StaffProfile } from '../../../runtime/auth/AuthContext';

export interface StaffProfileRowProps {
  readonly staffList: readonly StaffProfile[];
  readonly activeStaffId: string;
  readonly onSelectStaff: (staffId: string) => void;
}

export function StaffProfileRow({
  staffList,
  activeStaffId,
  onSelectStaff,
}: StaffProfileRowProps): React.JSX.Element {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '6px' }}>
      {staffList.map((staff) => {
        const isSelected = staff.id === activeStaffId;
        return (
          <button
            key={staff.id}
            type="button"
            onClick={() => onSelectStaff(staff.id)}
            aria-pressed={isSelected}
            className="nx-focusable"
            style={{
              minHeight: '62px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2px',
              padding: '6px 4px',
              borderRadius: '8px',
              border: `1px solid ${isSelected ? 'var(--nx-border-focus)' : 'var(--nx-border-default)'}`,
              backgroundColor: isSelected ? 'var(--nx-surface-selected)' : 'var(--nx-surface-subtle)',
              cursor: 'pointer',
            }}
          >
            <span aria-hidden="true" style={{ fontSize: '16px' }}>
              {staff.avatarIcon}
            </span>
            <NexusText
              variant="caption"
              style={{
                fontWeight: 600,
                maxWidth: '100%',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {staff.name.split(' ')[0]}
            </NexusText>
            <NexusText
              variant="caption"
              role="muted"
              style={{ fontSize: '9px', letterSpacing: '0.05em' }}
            >
              {staff.role}
            </NexusText>
          </button>
        );
      })}
    </div>
  );
}
