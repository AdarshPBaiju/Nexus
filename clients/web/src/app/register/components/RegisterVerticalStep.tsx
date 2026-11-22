'use client';

import React from 'react';
import { NexusBadge, NexusBox, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph, type GlyphName } from '../../components/NexusGlyph';

export interface RegisterVerticalStepProps {
  readonly selectedVertical: string;
  readonly onSelect: (vertical: string) => void;
}

const VERTICALS = [
  {
    code: 'CAFE_QSR',
    name: 'Café & Quick Service (QSR)',
    icon: 'local_cafe' as GlyphName,
    desc: 'High-speed counter ordering, hot modifiers, KDS barista routing, recipe BOM, and split-tender payments.',
    badge: 'Recommended',
  },
  {
    code: 'SPECIALTY_ROASTERY',
    name: 'Specialty Coffee & Roastery',
    icon: 'storefront' as GlyphName,
    desc: 'Bean batch lots, custom tasting notes, barista touch screen, wholesale packaging, and café counter.',
    badge: 'Artisan',
  },
  {
    code: 'GAMING_LOUNGE',
    name: 'Gaming Café & Esports Lounge',
    icon: 'terminal' as GlyphName,
    desc: 'Compound PC/Console/VR station timers, 2D floor canvas, single master commerce folio, and snack bar.',
    badge: 'Phase 4 Hybrid',
  },
  {
    code: 'BAKERY_DELI',
    name: 'Bakery & Fresh Delicatessen',
    icon: 'skillet' as GlyphName,
    desc: 'Daily production batches, cake customizers, barcode scale integration, and fresh display sales.',
    badge: 'Fresh Ops',
  },
];

export function RegisterVerticalStep({
  selectedVertical,
  onSelect,
}: RegisterVerticalStepProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '24px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <NexusStack gap="18px">
        <div>
          <NexusText variant="h3" style={{ margin: 0, fontWeight: 700 }}>
            Operating Vertical & Baseline Templates
          </NexusText>
          <NexusText variant="body" role="secondary" style={{ marginTop: '4px' }}>
            Choose your primary venue profile to automatically configure tax profiles, BOM structures, and POS layouts.
          </NexusText>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
          {VERTICALS.map((v) => {
            const isSelected = selectedVertical === v.code;
            return (
              <div
                key={v.code}
                onClick={() => onSelect(v.code)}
                style={{
                  padding: '16px',
                  borderRadius: '10px',
                  border: `2px solid ${isSelected ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                  backgroundColor: isSelected ? 'var(--nx-surface-selected, rgba(37, 99, 235, 0.05))' : 'var(--nx-surface-subtle)',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                  transition: 'border-color 0.12s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <NexusGlyph
                    name={v.icon}
                    size={24}
                    color={isSelected ? 'var(--nx-action-primary)' : 'var(--nx-text-primary)'}
                  />
                  <NexusBadge variant={isSelected ? 'success' : 'neutral'} label={v.badge} />
                </div>
                <NexusText variant="label" style={{ fontWeight: 700 }}>{v.name}</NexusText>
                <NexusText variant="caption" role="secondary" style={{ lineHeight: 1.4 }}>{v.desc}</NexusText>
              </div>
            );
          })}
        </div>
      </NexusStack>
    </NexusBox>
  );
}
