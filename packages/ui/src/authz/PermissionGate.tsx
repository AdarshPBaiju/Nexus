import React from 'react';
import { ClientAuthorizationStore } from '@nexus/contracts/authz/ClientAuthorizationStore';

export interface PermissionGateProps {
  readonly permission: string;
  readonly children: React.ReactNode;
  readonly fallback?: React.ReactNode;
}

/**
 * Declarative component gating views, actions, or widgets by fine-grained permission.
 */
export const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  children,
  fallback = null,
}) => {
  const store = ClientAuthorizationStore.getInstance();
  const hasAccess = store.can(permission);

  if (!hasAccess) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};
