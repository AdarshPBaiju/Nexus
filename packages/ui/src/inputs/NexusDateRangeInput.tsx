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
  testId,
}: NexusDateRangeInputProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
        <input
          type="date"
          value={value.startDate}
          disabled={isDisabled}
          onChange={(e) => onChange({ ...value, startDate: e.target.value })}
          style={{ height: '38px', padding: '0 8px', borderRadius: '6px', border: '1px solid var(--nx-border-default)' }}
        />
        <span>→</span>
        <input
          type="date"
          value={value.endDate}
          disabled={isDisabled}
          onChange={(e) => onChange({ ...value, endDate: e.target.value })}
          style={{ height: '38px', padding: '0 8px', borderRadius: '6px', border: '1px solid var(--nx-border-default)' }}
        />
      </div>
    </div>
  );
}
