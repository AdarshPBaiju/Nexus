import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';
import { NexusCheckbox } from './NexusCheckbox';

export interface NexusCheckboxGroupProps extends NexusControlProps<readonly string[]> {
  readonly options: readonly { readonly value: string; readonly label: string }[];
}

export function NexusCheckboxGroup({
  value = [],
  onChange,
  options,
  labelKey,
  isDisabled = false,
  testId,
}: NexusCheckboxGroupProps): React.JSX.Element {
  const toggle = (val: string, checked: boolean) => {
    if (checked) {
      onChange([...value, val]);
    } else {
      onChange(value.filter((v) => v !== val));
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-2)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      {options.map((opt) => (
        <NexusCheckbox
          key={opt.value}
          value={value.includes(opt.value)}
          labelKey={opt.label}
          isDisabled={isDisabled}
          onChange={(checked) => toggle(opt.value, checked)}
        />
      ))}
    </div>
  );
}
