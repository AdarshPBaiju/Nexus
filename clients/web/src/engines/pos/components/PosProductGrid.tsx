'use client';

import React from 'react';
import { NexusText } from '@nexus/ui';
import type { RichMenuItem } from '../cafeCatalogData';
import { PosProductCard } from './PosProductCard';
import { NexusGlyph } from '../../../app/components/NexusGlyph';

export interface PosProductGridProps {
  readonly products: readonly RichMenuItem[];
  readonly onAdd: (prod: RichMenuItem) => void;
  readonly onCustomize?: (prod: RichMenuItem) => void;
}

export function PosProductGrid({
  products,
  onAdd,
  onCustomize,
}: PosProductGridProps): React.JSX.Element {
  if (products.length === 0) {
    return (
      <div
        style={{
          height: '100%',
          minHeight: '180px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '4px',
          textAlign: 'center',
        }}
      >
        <NexusGlyph name="search_off" size={30} color="var(--nx-text-muted)" />
        <NexusText variant="label">No products match this filter</NexusText>
        <NexusText variant="caption" role="muted">
          Clear the search or switch category to continue.
        </NexusText>
      </div>
    );
  }

  return (
    <div className="nx-pos-grid">
      {products.map((prod) => (
        <PosProductCard key={prod.id} product={prod} onAdd={onAdd} onCustomize={onCustomize} />
      ))}
    </div>
  );
}
