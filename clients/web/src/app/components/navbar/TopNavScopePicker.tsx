'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph } from '../NexusGlyph';
import { useAuth } from '../../../runtime/auth/AuthContext';

export function TopNavScopePicker(): React.JSX.Element {
  const { activeTenant, availableTenants, switchTenant } = useAuth();
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

  const handleSelectTenant = (slug: string) => {
    switchTenant(slug);
    close();
  };

  return (
    <div ref={containerRef} style={{ position: 'relative' }}>
      <button
        type="button"
        onClick={toggleOpen}
        aria-expanded={isOpen}
        aria-haspopup="dialog"
        aria-label={`Current workspace: ${activeTenant.name}. Click to switch cloud workspace.`}
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
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', maxWidth: '280px', overflow: 'hidden' }}>
          <NexusText variant="label" style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>
            {activeTenant.name}
          </NexusText>
          <NexusText variant="caption" role="muted" style={{ whiteSpace: 'nowrap' }}>
            · {activeTenant.branchName}
          </NexusText>
        </span>
        <NexusBadge variant="neutral" label={activeTenant.region} />
        <NexusGlyph name={isOpen ? 'expand_less' : 'expand_more'} size={15} color="var(--nx-text-muted)" />
      </button>

      {isOpen && (
        <div
          role="dialog"
          aria-label="Cloud Workspaces Switcher"
          style={{
            position: 'absolute',
            top: 'calc(100% + 6px)',
            left: 0,
            width: '360px',
            backgroundColor: 'var(--nx-surface-card)',
            border: '1px solid var(--nx-border-default)',
            borderRadius: '10px',
            boxShadow: 'var(--nx-shadow-lg, 0 12px 32px rgba(0, 0, 0, 0.25))',
            zIndex: 1000,
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <NexusBox style={{ padding: '12px 14px', borderBottom: '1px solid var(--nx-border-subtle)', backgroundColor: 'var(--nx-surface-subtle)' }}>
            <NexusStack direction="row" align="center" justify="space-between">
              <div>
                <NexusText variant="label" style={{ fontWeight: 700 }}>Cloud SaaS Workspaces</NexusText>
                <NexusText variant="caption" role="muted" style={{ display: 'block', marginTop: '2px' }}>
                  Shared Regional Cell · Forced RLS Isolation
                </NexusText>
              </div>
              <NexusBadge variant="success" label="CLOUD PRO" />
            </NexusStack>
          </NexusBox>

          {/* Workspaces List */}
          <div style={{ maxHeight: '240px', overflowY: 'auto', padding: '6px' }}>
            {availableTenants.map((tenant) => {
              const isSelected = tenant.slug === activeTenant.slug;
              return (
                <button
                  key={tenant.slug}
                  type="button"
                  onClick={() => handleSelectTenant(tenant.slug)}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    border: '1px solid transparent',
                    backgroundColor: isSelected ? 'var(--nx-surface-selected)' : 'transparent',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'background-color 0.1s ease',
                  }}
                >
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <NexusStack direction="row" align="center" gap="6px">
                      <NexusText variant="label" style={{ fontWeight: isSelected ? 700 : 500 }}>
                        {tenant.name}
                      </NexusText>
                      {isSelected && <NexusBadge variant="success" label="Active" />}
                    </NexusStack>
                    <NexusText variant="caption" role="muted" style={{ display: 'block', fontSize: '11px', marginTop: '2px' }}>
                      {tenant.subdomain} · {tenant.region}
                    </NexusText>
                  </div>
                  {isSelected && <NexusGlyph name="check" size={16} color="var(--nx-action-primary)" />}
                </button>
              );
            })}
          </div>

          {/* Actions Footer */}
          <div style={{ padding: '8px 10px', borderTop: '1px solid var(--nx-border-subtle)', backgroundColor: 'var(--nx-surface-subtle)' }}>
            <NexusStack gap="4px">
              <Link href="/register" onClick={close} style={{ textDecoration: 'none' }}>
                <NexusBox style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px' }}>
                  <NexusGlyph name="domain_add" size={15} color="var(--nx-action-primary)" />
                  <NexusText variant="caption" style={{ fontWeight: 600, color: 'var(--nx-action-primary)' }}>
                    + Register New Cloud Organization
                  </NexusText>
                </NexusBox>
              </Link>
              <NexusStack direction="row" justify="space-between" style={{ padding: '4px 8px' }}>
                <Link href="/billing" onClick={close} style={{ textDecoration: 'none' }}>
                  <NexusText variant="caption" role="muted">Subscription & Quotas</NexusText>
                </Link>
                <Link href="/tenant/lifecycle" onClick={close} style={{ textDecoration: 'none' }}>
                  <NexusText variant="caption" role="muted">Governance & KMS</NexusText>
                </Link>
              </NexusStack>
            </NexusStack>
          </div>
        </div>
      )}
    </div>
  );
}
