import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusTextareaProps extends NexusControlProps<string> {
  readonly rows?: number;
  readonly maxLength?: number;
}

export function NexusTextarea({
  value,
  onChange,
  labelKey,
  placeholderKey,
  errorKey,
  isDisabled = false,
  isReadOnly = false,
  rows = 3,
  maxLength,
  testId,
}: NexusTextareaProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <textarea
        value={value}
        rows={rows}
        maxLength={maxLength}
        placeholder={placeholderKey}
        disabled={isDisabled}
        readOnly={isReadOnly}
        onChange={(e) => onChange(e.target.value)}
        style={{
          padding: 'var(--nx-space-2) var(--nx-space-3)',
          borderRadius: '6px',
          border: `1px solid ${errorKey ? 'var(--nx-status-danger)' : 'var(--nx-border-default)'}`,
          backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
          color: 'var(--nx-text-primary)',
          outline: 'none',
          resize: 'vertical',
        }}
      />
      {errorKey && <NexusText variant="caption">{errorKey}</NexusText>}
    </div>
  );
}
