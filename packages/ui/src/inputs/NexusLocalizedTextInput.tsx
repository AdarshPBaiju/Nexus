import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';
import { NexusBadge } from '../surfaces/NexusBadge';

export interface LocalizedStringMap {
  readonly [locale: string]: string;
}

export interface NexusLocalizedTextInputProps extends NexusControlProps<LocalizedStringMap> {
  readonly activeLocale: string;
  readonly availableLocales?: readonly string[];
  readonly translationStatus?: 'HUMAN' | 'MACHINE_TRANSLATED' | 'APPROVED';
}

export function NexusLocalizedTextInput({
  value,
  onChange,
  activeLocale,
  availableLocales = ['en', 'ar', 'es', 'fr', 'hi'],
  translationStatus = 'APPROVED',
  labelKey,
  isDisabled = false,
  size = 'md',
  testId,
}: NexusLocalizedTextInputProps): React.JSX.Element {
  const currentText = value[activeLocale] || '';

  const handleTextChange = (text: string) => {
    onChange({
      ...value,
      [activeLocale]: text,
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
        <div style={{ display: 'flex', gap: 'var(--nx-space-2)', alignItems: 'center' }}>
          <NexusBadge label={translationStatus} variant={translationStatus === 'APPROVED' ? 'success' : 'warning'} />
          <NexusText variant="caption" role="muted">({activeLocale.toUpperCase()})</NexusText>
        </div>
      </div>
      <input
        type="text"
        value={currentText}
        disabled={isDisabled}
        onChange={(e) => handleTextChange(e.target.value)}
        style={{
          height: size === 'sm' ? 'var(--input-height-compact, 32px)' : size === 'lg' ? '44px' : '38px',
          padding: '0 var(--nx-space-3)',
          borderRadius: '6px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--input-bg, var(--nx-surface-card))',
          color: 'var(--nx-text-primary)',
          outline: 'none',
        }}
      />
    </div>
  );
}
