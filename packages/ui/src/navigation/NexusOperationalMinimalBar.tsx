import React from 'react';
import { NexusText } from '../typography/NexusText';
import { NexusButton } from '../buttons/NexusButton';

export interface NexusOperationalMinimalBarProps {
  readonly stationName: string;
  readonly cashierName: string;
  readonly onExitKiosk?: () => void;
}

export function NexusOperationalMinimalBar({
  stationName,
  cashierName,
  onExitKiosk,
}: NexusOperationalMinimalBarProps): React.JSX.Element {
  return (
    <div
      style={{
        height: '38px',
        backgroundColor: 'var(--nx-surface-card)',
        borderBottom: '1px solid var(--nx-border-default)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 var(--nx-space-4)',
        userSelect: 'none',
      }}
    >
      <div style={{ display: 'flex', gap: 'var(--nx-space-4)', alignItems: 'center' }}>
        <NexusText variant="caption">Station: {stationName}</NexusText>
        <NexusText variant="caption" role="secondary">Cashier: {cashierName}</NexusText>
      </div>
      {onExitKiosk && (
        <NexusButton variant="outline" size="sm" onClick={onExitKiosk}>
          Lock / Exit
        </NexusButton>
      )}
    </div>
  );
}
