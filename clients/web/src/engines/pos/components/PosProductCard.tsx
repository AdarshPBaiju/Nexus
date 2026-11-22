'use client';

import React from 'react';
import { NexusBadge, NexusButton, NexusText } from '@nexus/ui';
import type { RichMenuItem } from '../cafeCatalogData';

export interface PosProductCardProps {
  readonly product: RichMenuItem;
  readonly onAdd: (prod: RichMenuItem) => void;
  readonly onCustomize?: (prod: RichMenuItem) => void;
}

export function PosProductCard({
  product,
  onAdd,
  onCustomize,
}: PosProductCardProps): React.JSX.Element {
  return (
    <div
      role="button"
      tabIndex={0}
      className="nx-pos-product nx-focusable"
      onClick={() => onAdd(product)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onAdd(product);
        }
      }}
      aria-label={`Add ${product.name} to order`}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', minHeight: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
          <NexusText
            variant="caption"
            role="muted"
            style={{ textTransform: 'uppercase', letterSpacing: '0.06em', fontSize: '9px' }}
          >
            {product.preparationStation}
          </NexusText>
          {product.badge && <NexusBadge variant="neutral" label={product.badge} />}
        </div>
        <NexusText
          variant="h4"
          style={{
            lineHeight: '17px',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {product.name}
        </NexusText>
        <NexusText
          variant="caption"
          role="muted"
          style={{
            display: '-webkit-box',
            WebkitLineClamp: 1,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
          }}
        >
          {product.description}
        </NexusText>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '6px',
          paddingTop: '8px',
          borderTop: '1px solid var(--nx-border-subtle)',
        }}
      >
        <NexusText variant="code" style={{ color: 'var(--nx-action-primary)', fontWeight: 700 }}>
          ${product.basePrice}
        </NexusText>
        <div style={{ display: 'flex', gap: '4px' }} onClick={(e) => e.stopPropagation()} role="presentation">
          {product.modifierGroups && product.modifierGroups.length > 0 && onCustomize && (
            <NexusButton
              variant="outline"
              size="sm"
              onClick={() => onCustomize(product)}
              ariaLabel={`Customize ${product.name}`}
            >
              <NexusText variant="caption">Custom</NexusText>
            </NexusButton>
          )}
          <NexusButton variant="primary" size="sm" onClick={() => onAdd(product)}>
            <NexusText variant="caption">Add</NexusText>
          </NexusButton>
        </div>
      </div>
    </div>
  );
}
