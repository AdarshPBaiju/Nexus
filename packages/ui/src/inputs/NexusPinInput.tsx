'use client';
import React, { useRef } from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';

export interface NexusPinInputProps extends NexusControlProps<string> {
  readonly length?: number;
  readonly isMasked?: boolean;
}

export function NexusPinInput({
  value,
  onChange,
  length = 4,
  isMasked = true,
  labelKey,
  isDisabled = false,
  size = 'md',
  testId,
}: NexusPinInputProps): React.JSX.Element {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

  const handleDigitChange = (index: number, digit: string) => {
    const chars = value.split('');
    chars[index] = digit;
    const nextVal = chars.join('').slice(0, length);
    onChange(nextVal);
    if (digit && index < length - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const boxSize = size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '54px' : '44px';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-2)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', gap: 'var(--nx-space-2)' }}>
        {Array.from({ length }).map((_, i) => (
          <input
            key={i}
            ref={(el) => { inputsRef.current[i] = el; }}
            type={isMasked ? 'password' : 'text'}
            maxLength={1}
            value={value[i] || ''}
            disabled={isDisabled}
            onChange={(e) => handleDigitChange(i, e.target.value)}
            style={{
              width: boxSize,
              height: boxSize,
              textAlign: 'center',
              fontSize: size === 'sm' ? '16px' : '20px',
              borderRadius: '6px',
              border: '1px solid var(--nx-border-default)',
              backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
              color: 'var(--nx-text-primary)',
              fontFamily: 'var(--input-font-mono, monospace)',
              outline: 'none',
            }}
          />
        ))}
      </div>
    </div>
  );
}
