import React from 'react';
import { NexusControlProps } from './types';
import { NexusIcon } from '../icons/NexusIcon';

export interface NexusSearchInputProps extends NexusControlProps<string> {
  readonly onClear?: () => void;
}

export function NexusSearchInput({
  value,
  onChange,
  placeholderKey = 'Search...',
  onClear,
  testId,
}: NexusSearchInputProps): React.JSX.Element {
  return (
    <div style={{ position: 'relative', display: 'flex', alignItems: 'center', width: '100%' }} data-testid={testId}>
      <span style={{ position: 'absolute', left: '10px', color: 'var(--nx-text-muted)' }}>
        <NexusIcon name="search" size="sm" />
      </span>
      <input
        type="search"
        value={value}
        placeholder={placeholderKey}
        onChange={(e) => onChange(e.target.value)}
        style={{
          height: '36px',
          padding: '0 32px',
          borderRadius: '6px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
          color: 'var(--nx-text-primary)',
          width: '100%',
          outline: 'none',
        }}
      />
      {value && (
        <button
          type="button"
          onClick={() => {
            onChange('');
            onClear?.();
          }}
          style={{ position: 'absolute', right: '10px', border: 'none', background: 'transparent', cursor: 'pointer' }}
        >
          ×
        </button>
      )}
    </div>
  );
}
