import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusCheckboxProps extends NexusControlProps<boolean> {
  readonly isIndeterminate?: boolean;
}

export function NexusCheckbox({
  value,
  onChange,
  labelKey,
  isDisabled = false,
  testId,
}: NexusCheckboxProps): React.JSX.Element {
  return (
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--nx-space-2)', cursor: isDisabled ? 'not-allowed' : 'pointer' }} data-testid={testId}>
      <input
        type="checkbox"
        checked={value}
        disabled={isDisabled}
        onChange={(e) => onChange(e.target.checked)}
        style={{ width: '18px', height: '18px', accentColor: 'var(--nx-action-primary)' }}
      />
      {labelKey && <NexusText variant="body">{labelKey}</NexusText>}
    </label>
  );
}
