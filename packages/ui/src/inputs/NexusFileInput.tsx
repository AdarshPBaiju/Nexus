import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusFileInputProps extends NexusControlProps<File | null> {
  readonly accept?: string;
}

export function NexusFileInput({
  value,
  onChange,
  labelKey,
  accept,
  isDisabled = false,
  testId,
}: NexusFileInputProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div
        style={{
          border: '2px dashed var(--nx-border-default)',
          borderRadius: '8px',
          padding: 'var(--nx-space-4)',
          textAlign: 'center',
          backgroundColor: 'var(--nx-surface-subtle)',
        }}
      >
        <input
          type="file"
          accept={accept}
          disabled={isDisabled}
          onChange={(e) => onChange(e.target.files?.[0] || null)}
          style={{ display: 'none' }}
          id="nexus-file-input"
        />
        <label htmlFor="nexus-file-input" style={{ cursor: 'pointer' }}>
          <NexusText variant="body">
            {value ? value.name : 'Click or drag file to upload'}
          </NexusText>
        </label>
      </div>
    </div>
  );
}
