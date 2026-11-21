import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusSliderProps extends NexusControlProps<number> {
  readonly min?: number;
  readonly max?: number;
  readonly step?: number;
}

export function NexusSlider({
  value,
  onChange,
  labelKey,
  min = 0,
  max = 100,
  step = 1,
  isDisabled = false,
  testId,
}: NexusSliderProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && (
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <NexusText variant="label">{labelKey}</NexusText>
          <NexusText variant="caption" tabular>{value.toString()}</NexusText>
        </div>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={isDisabled}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{ width: '100%', accentColor: 'var(--nx-action-primary)' }}
      />
    </div>
  );
}
