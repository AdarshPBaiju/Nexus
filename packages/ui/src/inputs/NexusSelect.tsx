import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface SelectOption<T = string> {
  readonly value: T;
  readonly label: string;
}

export interface NexusSelectProps<T = string> extends NexusControlProps<T> {
  readonly options: readonly SelectOption<T>[];
}

export function NexusSelect<T extends string = string>({
  value,
  onChange,
  options,
  labelKey,
  placeholderKey = 'Select an option...',
  isDisabled = false,
  errorKey,
  size = 'md',
  testId,
}: NexusSelectProps<T>): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <select
        value={value}
        disabled={isDisabled}
        onChange={(e) => onChange(e.target.value as T)}
        style={{
          height: size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '44px' : '38px',
          padding: '0 var(--nx-space-3)',
          borderRadius: '6px',
          border: `1px solid ${errorKey ? 'var(--nx-status-danger)' : 'var(--nx-border-default)'}`,
          backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
          color: 'var(--nx-text-primary)',
          outline: 'none',
        }}
      >
        <option value="" disabled>
          {placeholderKey}
        </option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {errorKey && <NexusText variant="caption">{errorKey}</NexusText>}
    </div>
  );
}
