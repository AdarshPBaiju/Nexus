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
  size = 'md',
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
          style={{
            height: size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '44px' : '38px',
            padding: '0 8px',
            borderRadius: '6px',
            border: '1px solid var(--nx-border-default)',
            backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
            color: 'var(--nx-text-primary)',
            fontFamily: 'var(--input-font-mono, monospace)',
            outline: 'none',
          }}
        />
        {timeZoneBadge && <NexusText variant="caption" role="muted">{timeZoneBadge}</NexusText>}
      </div>
    </div>
  );
}
