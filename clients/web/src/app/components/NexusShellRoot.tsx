'use client';

import React from 'react';
import { useAuth } from '../../runtime/auth/AuthContext';
import { CashierPinLoginScreen } from './CashierPinLoginScreen';

export function NexusShellRoot({
  children,
}: {
  readonly children: React.ReactNode;
}): React.JSX.Element {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <CashierPinLoginScreen />;
  }

  return <>{children}</>;
}
