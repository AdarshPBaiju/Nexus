'use client';

import React from 'react';
import { NexusGlyph } from '../NexusGlyph';

export interface PinKeypadProps {
  readonly onDigit: (digit: string) => void;
  readonly onClear: () => void;
  readonly onBackspace: () => void;
}

const DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9'];

export function PinKeypad({ onDigit, onClear, onBackspace }: PinKeypadProps): React.JSX.Element {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '7px' }}>
      {DIGITS.map((digit) => (
        <button
          key={digit}
          type="button"
          onClick={() => onDigit(digit)}
          className="nx-focusable"
          style={{
            height: '48px',
            borderRadius: '8px',
            border: '1px solid var(--nx-border-default)',
            backgroundColor: 'var(--nx-surface-subtle)',
            color: 'var(--nx-text-primary)',
            fontFamily: 'var(--font-mono)',
            fontSize: '18px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          {digit}
        </button>
      ))}
      <button
        type="button"
        onClick={onClear}
        className="nx-focusable"
        style={{
          height: '48px',
          borderRadius: '8px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'transparent',
          color: 'var(--nx-text-secondary)',
          fontFamily: 'var(--font-mono)',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        CLR
      </button>
      <button
        type="button"
        onClick={() => onDigit('0')}
        className="nx-focusable"
        style={{
          height: '48px',
          borderRadius: '8px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-subtle)',
          color: 'var(--nx-text-primary)',
          fontFamily: 'var(--font-mono)',
          fontSize: '18px',
          fontWeight: 600,
          cursor: 'pointer',
        }}
      >
        0
      </button>
      <button
        type="button"
        onClick={onBackspace}
        className="nx-focusable"
        aria-label="Backspace"
        style={{
          height: '48px',
          borderRadius: '8px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'transparent',
          color: 'var(--nx-text-secondary)',
          cursor: 'pointer',
        }}
      >
        <NexusGlyph name="backspace" size={18} />
      </button>
    </div>
  );
}
