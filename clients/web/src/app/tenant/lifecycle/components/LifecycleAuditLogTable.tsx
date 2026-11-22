'use client';

import React from 'react';
import { NexusBox, NexusStack, NexusText } from '@nexus/ui';
import type { AuditEvent } from '../types';

export interface LifecycleAuditLogTableProps {
  readonly events: readonly AuditEvent[];
}

export function LifecycleAuditLogTable({ events }: LifecycleAuditLogTableProps): React.JSX.Element {
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
            Forensic Audit & Lifecycle Event Trail
          </NexusText>
          <NexusText variant="caption" role="muted">
            Append-only immutable record of tenant lifecycle transitions, key rotations, and admin actions.
          </NexusText>
        </div>

        <div className="overflow-x-auto">
          <table className="nx-data-table" style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--nx-border-default)' }}>
                <th style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--nx-text-muted)' }}>TIMESTAMP</th>
                <th style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--nx-text-muted)' }}>ACTION</th>
                <th style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--nx-text-muted)' }}>ACTOR</th>
                <th style={{ padding: '8px 12px', fontSize: '11px', color: 'var(--nx-text-muted)' }}>AUDIT DETAILS</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt) => (
                <tr key={evt.id} style={{ borderBottom: '1px solid var(--nx-border-subtle)' }}>
                  <td style={{ padding: '10px 12px', fontSize: '12px', fontFamily: 'monospace' }}>
                    {new Date(evt.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td style={{ padding: '10px 12px', fontSize: '12px', fontWeight: 600 }}>
                    {evt.action}
                  </td>
                  <td style={{ padding: '10px 12px', fontSize: '12px', color: 'var(--nx-text-muted)' }}>
                    {evt.actor}
                  </td>
                  <td style={{ padding: '10px 12px', fontSize: '12px' }}>
                    {evt.detail}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </NexusStack>
    </NexusBox>
  );
}
