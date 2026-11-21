import React from 'react';
import { TablePaginationController } from './TablePaginationController';
import { NexusButton } from '../buttons/NexusButton';
import { NexusText } from '../typography/NexusText';

export interface NexusPaginationBarProps {
  readonly controller: TablePaginationController;
  readonly onNext?: () => void;
  readonly onPrevious?: () => void;
}

export function NexusPaginationBar({
  controller,
  onNext,
  onPrevious,
}: NexusPaginationBarProps): React.JSX.Element {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: 'var(--nx-space-2) var(--nx-space-4)',
        borderTop: '1px solid var(--nx-border-default)',
        backgroundColor: 'var(--nx-surface-card)',
      }}
    >
      <NexusText variant="caption" role="secondary">
        Rows per page: {controller.pageSize}
      </NexusText>
      <div style={{ display: 'flex', gap: 'var(--nx-space-2)' }}>
        <NexusButton variant="outline" size="sm" onClick={onPrevious}>
          Previous
        </NexusButton>
        <NexusButton variant="outline" size="sm" disabled={!controller.hasNext} onClick={onNext}>
          Next
        </NexusButton>
      </div>
    </div>
  );
}
