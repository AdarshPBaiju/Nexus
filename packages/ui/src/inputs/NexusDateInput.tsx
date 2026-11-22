import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusDateInputProps extends NexusControlProps<string> {
  readonly minDate?: string;
  readonly maxDate?: string;
}

export function NexusDateInput({
  value,
  onChange,
  labelKey,
  minDate,
  maxDate,
  isDisabled = false,
  size = 'md',
  testId,
}: NexusDateInputProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <input
        type="date"
        value={value}
        min={minDate}
        max={maxDate}
        disabled={isDisabled}
        onChange={(e) => onChange(e.target.value)}
        style={{
          height: size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '44px' : '38px',
          padding: '0 var(--nx-space-3)',
          borderRadius: '6px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
          color: 'var(--nx-text-primary)',
          fontFamily: 'var(--input-font-mono, monospace)',
          outline: 'none',
        }}
      />
    </div>
  );
}
