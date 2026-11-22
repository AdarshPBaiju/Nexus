import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface DateRange {
  readonly startDate: string;
  readonly endDate: string;
}

export interface NexusDateRangeInputProps extends NexusControlProps<DateRange> {}

export function NexusDateRangeInput({
  value,
  onChange,
  labelKey,
  isDisabled = false,
  size = 'md',
  testId,
}: NexusDateRangeInputProps): React.JSX.Element {
  const inputStyle: React.CSSProperties = {
    height: size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '44px' : '38px',
    padding: '0 8px',
    borderRadius: '6px',
    border: '1px solid var(--nx-border-default)',
    backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
    color: 'var(--nx-text-primary)',
    fontFamily: 'var(--input-font-mono, monospace)',
    outline: 'none',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
        <input
          type="date"
          value={value.startDate}
          disabled={isDisabled}
          onChange={(e) => onChange({ ...value, startDate: e.target.value })}
          style={inputStyle}
        />
        <span style={{ color: 'var(--nx-text-muted)' }}>→</span>
        <input
          type="date"
          value={value.endDate}
          disabled={isDisabled}
          onChange={(e) => onChange({ ...value, endDate: e.target.value })}
          style={inputStyle}
        />
      </div>
    </div>
  );
}
