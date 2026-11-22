'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph, type GlyphName } from '../components/NexusGlyph';
import type { PluginPackage } from './types';

export interface PluginDetailModalProps {
  readonly plugin: PluginPackage | null;
  readonly isOpen: boolean;
  readonly onClose: () => void;
}

export function PluginDetailModal({
  plugin,
  isOpen,
  onClose,
}: PluginDetailModalProps): React.JSX.Element | null {
  if (!plugin || !isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.65)',
        backdropFilter: 'blur(4px)',
        padding: '16px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '560px',
          borderRadius: '12px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
        }}
      >
        <NexusStack gap="16px">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '8px',
                backgroundColor: 'var(--nx-surface-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <NexusGlyph name={(plugin.icon as GlyphName) || 'extension'} size={24} />
            </div>
            <div>
              <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>{plugin.name}</NexusText>
              <NexusText variant="code" role="muted">{plugin.code} — {plugin.tier}</NexusText>
            </div>
          </div>

          <NexusText variant="body" role="secondary">{plugin.description}</NexusText>

          <NexusBox
            style={{
              padding: '12px 14px',
              borderRadius: '8px',
              backgroundColor: 'var(--nx-surface-subtle)',
              border: '1px solid var(--nx-border-subtle)',
            }}
          >
            <NexusStack gap="8px">
              <NexusText variant="label" style={{ fontWeight: 600 }}>Capability Architectural Invariants</NexusText>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                <div>
                  <NexusText variant="caption" role="muted">EXECUTION SURFACE</NexusText>
                  <NexusText variant="body" style={{ fontWeight: 600 }}>{plugin.execution_surface}</NexusText>
                </div>
                <div>
                  <NexusText variant="caption" role="muted">INSTALLATION MODEL</NexusText>
                  <NexusText variant="body" style={{ fontWeight: 600 }}>Declarative Enablement (Zero Restart)</NexusText>
                </div>
                <div>
                  <NexusText variant="caption" role="muted">SEMVER VERSION</NexusText>
                  <NexusText variant="body" className="nx-numeric">v{plugin.version}</NexusText>
                </div>
                <div>
                  <NexusText variant="caption" role="muted">ACTIVE STATUS</NexusText>
                  <NexusBadge
                    variant={plugin.status === 'ACTIVE' ? 'success' : plugin.status === 'DRAINING' ? 'warning' : 'neutral'}
                    label={plugin.status}
                  />
                </div>
              </div>
            </NexusStack>
          </NexusBox>

          {plugin.dependencies.length > 0 && (
            <NexusBox>
              <NexusText variant="label" style={{ fontWeight: 600, marginBottom: '6px' }}>
                Upstream Module Dependencies
              </NexusText>
              <div style={{ display: 'flex', gap: '8px' }}>
                {plugin.dependencies.map((dep) => (
                  <NexusBadge key={dep} variant="info" label={dep} />
                ))}
              </div>
            </NexusBox>
          )}

          <NexusBox
            style={{
              padding: '10px 12px',
              borderRadius: '6px',
              backgroundColor: 'var(--nx-status-info-subtle, rgba(2, 132, 199, 0.1))',
              border: '1px solid var(--nx-status-info)',
            }}
          >
            <NexusText variant="caption" role="primary">
              <strong>Draining Uninstall Law:</strong> Disabling this package sets status to DRAINING, safely allowing existing folios, kitchen bump orders, and payments to complete while blocking new incoming requests.
            </NexusText>
          </NexusBox>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', paddingTop: '10px' }}>
            <NexusButton variant="secondary" onClick={onClose}>
              Close Inspector
            </NexusButton>
          </div>
        </NexusStack>
      </div>
    </div>
  );
}
