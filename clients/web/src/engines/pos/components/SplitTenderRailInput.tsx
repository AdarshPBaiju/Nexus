'use client';

import React from 'react';
import { NexusButton, NexusText, NexusTextInput } from '@nexus/ui';

export interface SplitTenderRailInputProps {
  readonly label: string;
  readonly hint: string;
  readonly value: string;
  readonly onChange: (v: string) => void;
  readonly onFull: () => void;
}

export function SplitTenderRailInput({
  label,
  hint,
  value,
  onChange,
  onFull,
}: SplitTenderRailInputProps): React.JSX.Element {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 10px',
        borderRadius: '8px',
        border: '1px solid var(--nx-border-subtle)',
        backgroundColor: 'var(--nx-surface-subtle)',
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <NexusText variant="label">{label}</NexusText>
        <NexusText variant="caption" role="muted" style={{ display: 'block' }}>
          {hint}
        </NexusText>
      </div>
      <div style={{ width: '110px' }}>
        <NexusTextInput
          placeholderKey="0.00"
          value={value}
          onChange={onChange}
        />
      </div>
      <NexusButton variant="outline" size="sm" onClick={onFull}>
        <NexusText variant="caption">Full</NexusText>
      </NexusButton>
    </div>
  );
}
