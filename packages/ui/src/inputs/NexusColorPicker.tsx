import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusColorPickerProps extends NexusControlProps<string> {
  readonly presetColors?: readonly string[];
}

export function NexusColorPicker({
  value,
  onChange,
  labelKey,
  presetColors = ['#2563EB', '#16A34A', '#D97706', '#DC2626', '#0284C7', '#8B5CF6'],
  isDisabled = false,
  testId,
}: NexusColorPickerProps): React.JSX.Element {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
        <input
          type="color"
          value={value}
          disabled={isDisabled}
          onChange={(e) => onChange(e.target.value)}
          style={{ width: '38px', height: '38px', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
        />
        {presetColors.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => onChange(c)}
            disabled={isDisabled}
            style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: c, border: value === c ? '2px solid var(--nx-border-focus)' : 'none', cursor: 'pointer' }}
          />
        ))}
      </div>
    </div>
  );
}
