'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph, type GlyphName } from '../components/NexusGlyph';
import type { PluginPackage } from './types';

export interface PluginCardProps {
  readonly plugin: PluginPackage;
  readonly onToggle: (code: string, action: 'INSTALL' | 'ENABLE' | 'DRAIN' | 'ARCHIVE') => void;
  readonly onOpenDetails: (plugin: PluginPackage) => void;
  readonly isBusy: boolean;
}

export function PluginCard({
  plugin,
  onToggle,
  onOpenDetails,
  isBusy,
}: PluginCardProps): React.JSX.Element {
  const isInstalled = plugin.status === 'ACTIVE';
  const isDraining = plugin.status === 'DRAINING';

  const surfaceBadge = {
    WEB_ALL: { label: 'Web & Desktop', variant: 'neutral' as const },
    DESKTOP_ONLY: { label: 'Desktop Native Only', variant: 'warning' as const },
    HYBRID_WEB_DESKTOP: { label: 'Hybrid Web+Desktop', variant: 'info' as const },
  }[plugin.execution_surface];

  return (
    <NexusBox
      style={{
        padding: '16px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: `1px solid ${isInstalled ? 'var(--nx-border-default)' : 'var(--nx-border-subtle)'}`,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        gap: '14px',
        transition: 'transform 0.12s ease, border-color 0.12s ease',
      }}
    >
      <NexusStack gap="10px">
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '8px',
                backgroundColor: isInstalled ? 'var(--nx-action-primary)' : 'var(--nx-surface-subtle)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <NexusGlyph
                name={(plugin.icon as GlyphName) || 'extension'}
                size={20}
                color={isInstalled ? 'var(--nx-action-text)' : 'var(--nx-text-muted)'}
              />
            </div>
            <div>
              <NexusText variant="label" style={{ fontWeight: 700 }}>
                {plugin.name}
              </NexusText>
              <NexusText variant="code" role="muted" style={{ fontSize: '11px' }}>
                {plugin.code} v{plugin.version}
              </NexusText>
            </div>
          </div>

          <NexusBadge
            variant={isInstalled ? 'success' : isDraining ? 'warning' : 'neutral'}
            label={plugin.status}
          />
        </div>

        <NexusText
          variant="body"
          role="secondary"
          style={{
            fontSize: '13px',
            lineHeight: 1.45,
            minHeight: '40px',
          }}
        >
          {plugin.description}
        </NexusText>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <NexusBadge variant={surfaceBadge.variant} label={surfaceBadge.label} />
          <NexusBadge variant="neutral" label={plugin.category} />
          {plugin.dependencies.length > 0 && (
            <NexusText variant="caption" role="muted" style={{ fontSize: '11px' }}>
              Requires: {plugin.dependencies.join(', ')}
            </NexusText>
          )}
        </div>
      </NexusStack>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', paddingTop: '8px', borderTop: '1px solid var(--nx-border-subtle)' }}>
        <NexusButton
          variant="ghost"
          size="sm"
          onClick={() => onOpenDetails(plugin)}
        >
          Details
        </NexusButton>

        {isInstalled ? (
          <NexusButton
            variant="destructive"
            size="sm"
            disabled={isBusy}
            onClick={() => onToggle(plugin.code, 'DRAIN')}
          >
            Drain & Uninstall
          </NexusButton>
        ) : isDraining ? (
          <div style={{ display: 'flex', gap: '6px' }}>
            <NexusButton
              variant="secondary"
              size="sm"
              disabled={isBusy}
              onClick={() => onToggle(plugin.code, 'ENABLE')}
            >
              Resume
            </NexusButton>
            <NexusButton
              variant="destructive"
              size="sm"
              disabled={isBusy}
              onClick={() => onToggle(plugin.code, 'ARCHIVE')}
            >
              Archive
            </NexusButton>
          </div>
        ) : (
          <NexusButton
            variant="primary"
            size="sm"
            disabled={isBusy}
            onClick={() => onToggle(plugin.code, 'INSTALL')}
          >
            Install Feature
          </NexusButton>
        )}
      </div>
    </NexusBox>
  );
}
