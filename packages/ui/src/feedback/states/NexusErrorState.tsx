import React from 'react';
import { NexusText } from '../../typography/NexusText';
import { NexusButton } from '../../buttons/NexusButton';
import { NexusStack } from '../../surfaces/NexusStack';

export interface NexusErrorStateProps {
  readonly message?: string;
  readonly requestId?: string;
  readonly onRetry?: () => void;
  readonly className?: string;
}

export function NexusErrorState({
  message = 'An unexpected error occurred.',
  requestId,
  onRetry,
  className = '',
}: NexusErrorStateProps): React.JSX.Element {
  return (
    <div style={{ padding: 'var(--nx-space-8) var(--nx-space-4)', textAlign: 'center' }} className={className}>
      <NexusStack align="center" gap="var(--nx-space-3)">
        <NexusText variant="h3">Operation Failed</NexusText>
        <NexusText role="secondary">{message}</NexusText>
        {requestId && (
          <NexusText variant="code" role="muted">
            Request-ID: {requestId}
          </NexusText>
        )}
        {onRetry && (
          <NexusButton variant="primary" onClick={onRetry}>
            Retry Operation
          </NexusButton>
        )}
      </NexusStack>
    </div>
  );
}
