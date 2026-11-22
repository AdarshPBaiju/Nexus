import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';
import { NexusBadge } from '../surfaces/NexusBadge';

export interface NexusMultiSelectProps extends NexusControlProps<readonly string[]> {
  readonly options: readonly { readonly value: string; readonly label: string }[];
}

export function NexusMultiSelect({
  value = [],
  onChange,
  options,
  labelKey,
  isDisabled = false,
  testId,
}: NexusMultiSelectProps): React.JSX.Element {
  const toggle = (val: string) => {
    if (isDisabled) return;
    if (value.includes(val)) {
      onChange(value.filter((v) => v !== val));
    } else {
      onChange([...value, val]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 'var(--nx-space-2)',
          minHeight: '38px',
          padding: 'var(--nx-space-2)',
          border: '1px solid var(--nx-border-default)',
          borderRadius: '6px',
          backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
        }}
      >
        {options.map((opt) => {
          const selected = value.includes(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => toggle(opt.value)}
              disabled={isDisabled}
              style={{ border: 'none', background: 'transparent', padding: 0, cursor: 'pointer' }}
            >
              <NexusBadge label={opt.label} variant={selected ? 'info' : 'neutral'} />
            </button>
          );
        })}
      </div>
    </div>
  );
}
