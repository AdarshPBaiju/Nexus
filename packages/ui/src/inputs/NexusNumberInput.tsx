import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusNumberInputProps extends NexusControlProps<number> {
  readonly min?: number;
  readonly max?: number;
  readonly step?: number;
  readonly precision?: number;
}

export function NexusNumberInput({
  value,
  onChange,
  labelKey,
  errorKey,
  isDisabled = false,
  isReadOnly = false,
  min,
  max,
  step = 1,
  size = 'md',
  testId,
}: NexusNumberInputProps): React.JSX.Element {
  const handleStep = (delta: number) => {
    if (isDisabled || isReadOnly) return;
    let next = value + delta;
    if (min !== undefined && next < min) next = min;
    if (max !== undefined && next > max) next = max;
    onChange(next);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <input
          type="number"
          value={value}
          min={min}
          max={max}
          step={step}
          disabled={isDisabled}
          readOnly={isReadOnly}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          className="nx-numeric"
          style={{
            height: size === 'sm' ? '32px' : '38px',
            padding: '0 var(--nx-space-3)',
            borderRadius: '6px 0 0 6px',
            border: '1px solid var(--nx-border-default)',
            backgroundColor: 'var(--nx-surface-card)',
            color: 'var(--nx-text-primary)',
            outline: 'none',
            flex: 1,
          }}
        />
        <button
          type="button"
          onClick={() => handleStep(-step)}
          disabled={isDisabled || isReadOnly}
          style={{ padding: '0 8px', height: '38px', border: '1px solid var(--nx-border-default)', borderLeft: 'none' }}
        >
          -
        </button>
        <button
          type="button"
          onClick={() => handleStep(step)}
          disabled={isDisabled || isReadOnly}
          style={{ padding: '0 8px', height: '38px', border: '1px solid var(--nx-border-default)', borderLeft: 'none', borderRadius: '0 6px 6px 0' }}
        >
          +
        </button>
      </div>
      {errorKey && <NexusText variant="caption">{errorKey}</NexusText>}
    </div>
  );
}
