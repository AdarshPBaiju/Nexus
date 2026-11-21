import React from 'react';
import { NexusText } from '../../typography/NexusText';
import { NexusButton } from '../../buttons/NexusButton';
import { NexusStack } from '../../surfaces/NexusStack';

export interface NexusEmptyStateProps {
  readonly title: string;
  readonly description: string;
  readonly actionLabel?: string;
  readonly onAction?: () => void;
  readonly className?: string;
}

export function NexusEmptyState({
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}: NexusEmptyStateProps): React.JSX.Element {
  return (
    <div style={{ padding: 'var(--nx-space-12) var(--nx-space-4)', textAlign: 'center' }} className={className}>
      <NexusStack align="center" gap="var(--nx-space-3)">
        <NexusText variant="h3">{title}</NexusText>
        <NexusText role="secondary">{description}</NexusText>
        {actionLabel && onAction && (
          <NexusButton variant="primary" onClick={onAction}>
            {actionLabel}
          </NexusButton>
        )}
      </NexusStack>
    </div>
  );
}
