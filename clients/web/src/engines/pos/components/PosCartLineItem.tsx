'use client';

import React from 'react';
import { NexusButton, NexusText } from '@nexus/ui';
import type { PosCartItem } from '../types';
import { NexusGlyph } from '../../../app/components/NexusGlyph';

export interface PosCartLineItemProps {
  readonly item: PosCartItem;
  readonly onUpdateQuantity: (id: string, delta: number) => void;
  readonly onRequestVoid: (id: string) => void;
}

export function PosCartLineItem({
  item,
  onUpdateQuantity,
  onRequestVoid,
}: PosCartLineItemProps): React.JSX.Element {
  const lineTotal = (parseFloat(item.unitPrice) * item.quantity).toFixed(2);

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) auto auto auto',
        alignItems: 'center',
        gap: '8px',
        padding: '7px 8px',
        borderRadius: '7px',
        border: '1px solid var(--nx-border-subtle)',
        backgroundColor: 'var(--nx-surface-subtle)',
      }}
    >
      <div style={{ minWidth: 0 }}>
        <NexusText
          variant="label"
          style={{
            display: 'block',
            fontWeight: 600,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {item.name}
        </NexusText>
        {item.selectedModifiers && item.selectedModifiers.length > 0 && (
          <NexusText
            variant="caption"
            role="muted"
            style={{
              fontSize: '10px',
              display: 'block',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {item.selectedModifiers.map((m) => m.name).join(', ')}
          </NexusText>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
        <NexusButton
          variant="outline"
          size="sm"
          onClick={() => onUpdateQuantity(item.id, -1)}
          ariaLabel={`Decrease ${item.name} quantity`}
        >
          -
        </NexusButton>
        <NexusText
          variant="code"
          tabular
          style={{ width: '22px', textAlign: 'center', fontWeight: 600 }}
        >
          {item.quantity}
        </NexusText>
        <NexusButton
          variant="outline"
          size="sm"
          onClick={() => onUpdateQuantity(item.id, 1)}
          ariaLabel={`Increase ${item.name} quantity`}
        >
          +
        </NexusButton>
      </div>

      <NexusText
        variant="code"
        tabular
        style={{
          width: '54px',
          textAlign: 'end',
          fontWeight: 700,
          color: 'var(--nx-text-primary)',
        }}
      >
        ${lineTotal}
      </NexusText>

      <button
        type="button"
        onClick={() => onRequestVoid(item.id)}
        aria-label={`Void line item ${item.name}`}
        title="Void line (requires manager PIN)"
        className="nx-focusable"
        style={{
          border: 'none',
          background: 'transparent',
          color: 'var(--nx-status-danger-text)',
          cursor: 'pointer',
          padding: '2px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <NexusGlyph name="close" size={14} />
      </button>
    </div>
  );
}
