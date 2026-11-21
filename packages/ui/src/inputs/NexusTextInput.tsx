import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusTextInputProps extends NexusControlProps<string> {
  readonly prefixIcon?: React.ReactNode;
  readonly suffixIcon?: React.ReactNode;
  readonly maxLength?: number;
  readonly isClearable?: boolean;
}

export function NexusTextInput({
  value,
  onChange,
  labelKey,
  placeholderKey,
  errorKey,
  isDisabled = false,
  isReadOnly = false,
  maxLength,
  isClearable = true,
  size = 'md',
  testId,
}: NexusTextInputProps): React.JSX.Element {
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: 'var(--nx-space-1)',
  };

  const inputStyle: React.CSSProperties = {
    height: size === 'sm' ? '32px' : size === 'lg' ? '44px' : '38px',
    padding: '0 var(--nx-space-3)',
    borderRadius: '6px',
    border: `1px solid ${errorKey ? 'var(--nx-status-danger)' : 'var(--nx-border-default)'}`,
    backgroundColor: 'var(--nx-surface-card)',
    color: 'var(--nx-text-primary)',
    outline: 'none',
    width: '100%',
  };

  return (
    <div style={containerStyle} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <input
          type="text"
          value={value}
          disabled={isDisabled}
          readOnly={isReadOnly}
          maxLength={maxLength}
          placeholder={placeholderKey}
          onChange={(e) => onChange(e.target.value)}
          style={inputStyle}
        />
        {isClearable && value && !isDisabled && !isReadOnly && (
          <button
            type="button"
            onClick={() => onChange('')}
            style={{
              position: 'absolute',
              right: '8px',
              border: 'none',
              background: 'transparent',
              cursor: 'pointer',
              color: 'var(--nx-text-muted)',
            }}
          >
            ×
          </button>
        )}
      </div>
      {errorKey && <NexusText variant="caption" role="muted">{errorKey}</NexusText>}
    </div>
  );
}
