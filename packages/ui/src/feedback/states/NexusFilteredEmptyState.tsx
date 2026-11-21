import React from 'react';
import { NexusText } from '../../typography/NexusText';
import { NexusButton } from '../../buttons/NexusButton';
import { NexusStack } from '../../surfaces/NexusStack';

export interface NexusFilteredEmptyStateProps {
  readonly onClearFilters: () => void;
  readonly className?: string;
}

export function NexusFilteredEmptyState({
  onClearFilters,
  className = '',
}: NexusFilteredEmptyStateProps): React.JSX.Element {
  return (
    <div style={{ padding: 'var(--nx-space-8) var(--nx-space-4)', textAlign: 'center' }} className={className}>
      <NexusStack align="center" gap="var(--nx-space-3)">
        <NexusText variant="h3">No Matching Results</NexusText>
        <NexusText role="secondary">No records match the active filter criteria.</NexusText>
        <NexusButton variant="outline" onClick={onClearFilters}>
          Clear Filters
        </NexusButton>
      </NexusStack>
    </div>
  );
}
