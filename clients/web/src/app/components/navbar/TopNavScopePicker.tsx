'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { NexusBadge, NexusBox, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph } from '../NexusGlyph';
import { useAuth } from '../../../runtime/auth/AuthContext';

export function TopNavScopePicker(): React.JSX.Element {
  const { activeTenant, session } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const toggleOpen = useCallback(() => setIsOpen((prev) => !prev), []);
  const close = useCallback(() => setIsOpen(false), []);

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        close();
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') close();
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, close]);

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <button
        type="button"
        onClick={toggleOpen}
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        aria-label={`Current workspace: ${activeTenant.name}. Click to view workspace security and station scope.`}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          height: '32px',
          padding: '0 10px',
          borderRadius: '7px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: isOpen ? 'var(--nx-surface-selected)' : 'var(--nx-surface-subtle)',
          cursor: 'pointer',
          outline: 'none',
          transition: 'background-color 0.15s ease, border-color 0.15s ease',
        }}
      >
        <NexusGlyph name="storefront" size={15} color="var(--nx-action-primary)" />
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', maxWidth: '300px', overflow: 'hidden' }}>
          <NexusText variant="label" style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
            {activeTenant.name}
          </NexusText>
          <NexusText variant="caption" role="muted" style={{ whiteSpace: 'nowrap' }}>
            · {activeTenant.branchName}
          </NexusText>
        </span>
        <NexusBadge variant="neutral" label={activeTenant.region} />
        <NexusBadge variant="success" label="RLS ISOLATED" />
        <NexusGlyph name={isOpen ? 'expand_less' : 'expand_more'} size={15} color="var(--nx-text-muted)" />
      </button>

      {isOpen && (
        <div
          role="dialog"
          aria-label="Workspace Scope and Security Details"
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            width: '380px',
            backgroundColor: 'var(--nx-surface-card)',
            border: '1px solid var(--nx-border-default)',
            borderRadius: '10px',
            boxShadow: 'var(--nx-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.25))',
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <NexusBox style={{ padding: '14px 16px', borderBottom: '1px solid var(--nx-border-subtle)', backgroundColor: 'var(--nx-surface-subtle)' }}>
            <NexusStack direction="row" align="center" justify="space-between">
              <div>
                <NexusText variant="label" style={{ fontWeight: 700, fontSize: '14px' }}>{activeTenant.name}</NexusText>
                <NexusText variant="caption" style={{ display: 'block', color: 'var(--nx-action-primary)', fontFamily: 'var(--font-mono, monospace)', marginTop: '2px' }}>
                  https://{activeTenant.subdomain}
                </NexusText>
              </div>
              <NexusBadge variant="success" label={activeTenant.tier} />
            </NexusStack>
          </NexusBox>

          {/* Tenant Security & Station Telemetry */}
          <div style={{ padding: '14px 16px' }}>
            <NexusStack gap="10px">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <NexusText variant="caption" role="muted">Store Location:</NexusText>
                <NexusText variant="label" style={{ fontWeight: 600 }}>{activeTenant.branchName}</NexusText>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <NexusText variant="caption" role="muted">Terminal Workstation:</NexusText>
                <NexusText variant="caption" style={{ fontFamily: 'var(--font-mono, monospace)' }}>{session.workstationId || 'WS-POS-01'}</NexusText>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <NexusText variant="caption" role="muted">Cloud Data Residency:</NexusText>
                <NexusBadge variant="neutral" label={`${activeTenant.region} · Sovereign Cell`} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <NexusText variant="caption" role="muted">Database Isolation:</NexusText>
                <NexusBadge variant="success" label="Forced PostgreSQL RLS (NOBYPASSRLS)" />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <NexusText variant="caption" role="muted">Regional KMS Envelope:</NexusText>
                <NexusText variant="caption" style={{ fontFamily: 'var(--font-mono, monospace)' }}>AES-256-GCM (AAD Bound)</NexusText>
              </div>
            </NexusStack>
          </div>

          {/* Quick Tenant Workspace Actions */}
          <div style={{ padding: '10px 14px', borderTop: '1px solid var(--nx-border-subtle)', backgroundColor: 'var(--nx-surface-subtle)' }}>
            <NexusStack gap="6px">
              <Link href="/billing" onClick={close} style={{ textDecoration: 'none' }}>
                <NexusBox style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', borderRadius: '6px' }}>
                  <NexusText variant="caption" style={{ fontWeight: 600, color: 'var(--nx-text-primary)' }}>
                    Subscription, Invoices & Station Licenses →
                  </NexusText>
                  <NexusBadge variant="neutral" label="PRO" />
                </NexusBox>
              </Link>
              <Link href="/tenant/lifecycle" onClick={close} style={{ textDecoration: 'none' }}>
                <NexusBox style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px', borderRadius: '6px' }}>
                  <NexusText variant="caption" style={{ fontWeight: 600, color: 'var(--nx-text-primary)' }}>
                    Governance, Maintenance Drain & KMS Key Rotation →
                  </NexusText>
                  <NexusBadge variant="success" label="ACTIVE" />
                </NexusBox>
              </Link>
            </NexusStack>
          </div>
        </div>
      )}
    </div>
  );
}
