import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusTimeInputProps extends NexusControlProps<string> {
  readonly timeZoneBadge?: string;
}

export function NexusTimeInput({
  value,
  onChange,
  labelKey,
  timeZoneBadge,
  isDisabled = false,
  testId,
}: NexusTimeInputProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
        <input
          type="time"
          value={value}
          disabled={isDisabled}
          onChange={(e) => onChange(e.target.value)}
          style={{ height: '38px', padding: '0 8px', borderRadius: '6px', border: '1px solid var(--nx-border-default)' }}
        />
        {timeZoneBadge && <NexusText variant="caption" role="muted">{timeZoneBadge}</NexusText>}
      </div>
    </div>
  );
}
