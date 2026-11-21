import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusRadioGroupProps extends NexusControlProps<string> {
  readonly options: readonly { readonly value: string; readonly label: string }[];
  readonly name: string;
}

export function NexusRadioGroup({
  value,
  onChange,
  options,
  name,
  labelKey,
  isDisabled = false,
  testId,
}: NexusRadioGroupProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-2)' }} data-testid={testId} role="radiogroup">
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      {options.map((opt) => (
        <label key={opt.value} style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--nx-space-2)', cursor: isDisabled ? 'not-allowed' : 'pointer' }}>
          <input
            type="radio"
            name={name}
            value={opt.value}
            checked={value === opt.value}
            disabled={isDisabled}
            onChange={() => onChange(opt.value)}
            style={{ accentColor: 'var(--nx-action-primary)' }}
          />
          <NexusText variant="body">{opt.label}</NexusText>
        </label>
      ))}
    </div>
  );
}
