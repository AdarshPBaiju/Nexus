import React from 'react';
import { NexusControlProps } from './types';
import { NexusText } from '../typography/NexusText';
import { Money } from '@nexus/contracts';

export interface NexusMoneyInputProps extends NexusControlProps<Money> {
  readonly supportedCurrencies?: readonly string[];
}

export function NexusMoneyInput({
  value,
  onChange,
  labelKey,
  supportedCurrencies = ['USD', 'EUR', 'GBP', 'INR', 'AED'],
  isDisabled = false,
  testId,
}: NexusMoneyInputProps): React.JSX.Element {
  const handleAmountChange = (amtStr: string) => {
    try {
      onChange(new Money(amtStr || '0.00', value.currency));
    } catch {
      // Ignore invalid partial input
    }
  };

  const handleCurrencyChange = (curr: string) => {
    onChange(new Money(value.amount, curr));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--nx-space-1)' }} data-testid={testId}>
      {labelKey && <NexusText variant="label">{labelKey}</NexusText>}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <select
          value={value.currency}
          disabled={isDisabled}
          onChange={(e) => handleCurrencyChange(e.target.value)}
          style={{ height: '38px', padding: '0 8px', borderRadius: '6px 0 0 6px', border: '1px solid var(--nx-border-default)', backgroundColor: 'var(--nx-surface-subtle)' }}
        >
          {supportedCurrencies.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <input
          type="text"
          value={value.amount}
          disabled={isDisabled}
          onChange={(e) => handleAmountChange(e.target.value)}
          className="nx-numeric"
          style={{ height: '38px', padding: '0 8px', borderRadius: '0 6px 6px 0', border: '1px solid var(--nx-border-default)', borderLeft: 'none', flex: 1 }}
        />
      </div>
    </div>
  );
}
