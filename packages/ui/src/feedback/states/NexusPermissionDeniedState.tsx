import React from 'react';
import { NexusText } from '../../typography/NexusText';
import { NexusStack } from '../../surfaces/NexusStack';

export interface NexusPermissionDeniedStateProps {
  readonly requiredPermission?: string;
  readonly className?: string;
}

export function NexusPermissionDeniedState({
  requiredPermission,
  className = '',
}: NexusPermissionDeniedStateProps): React.JSX.Element {
  return (
    <div style={{ padding: 'var(--nx-space-12) var(--nx-space-4)', textAlign: 'center' }} className={className}>
      <NexusStack align="center" gap="var(--nx-space-3)">
        <NexusText variant="h3">Access Denied (403)</NexusText>
        <NexusText role="secondary">
          You do not have the required authorization to view or execute this resource.
        </NexusText>
        {requiredPermission && (
          <NexusText variant="code" role="muted">
            Missing Permission: {requiredPermission}
          </NexusText>
        )}
      </NexusStack>
    </div>
  );
}
