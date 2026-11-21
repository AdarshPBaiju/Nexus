import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusSwitchProps extends NexusControlProps<boolean> {}

export function NexusSwitch({
  value,
  onChange,
  labelKey,
  isDisabled = false,
  testId,
}: NexusSwitchProps): React.JSX.Element {
  return (
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--nx-space-3)', cursor: isDisabled ? 'not-allowed' : 'pointer' }} data-testid={testId}>
      <button
        type="button"
        role="switch"
        aria-checked={value}
        disabled={isDisabled}
        onClick={() => onChange(!value)}
        style={{
          width: '40px',
          height: '24px',
          borderRadius: '12px',
          backgroundColor: value ? 'var(--nx-action-primary)' : 'var(--nx-surface-subtle)',
          border: '1px solid var(--nx-border-default)',
          position: 'relative',
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          padding: 0,
        }}
      >
        <span
          style={{
            display: 'block',
            width: '18px',
            height: '18px',
            borderRadius: '50%',
            backgroundColor: '#FFFFFF',
            position: 'absolute',
            top: '2px',
            left: value ? '18px' : '2px',
            transition: 'left 0.15s ease',
          }}
        />
      </button>
      {labelKey && <NexusText variant="body">{labelKey}</NexusText>}
    </label>
  );
}
