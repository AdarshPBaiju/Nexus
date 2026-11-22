'use client';

import React, { createContext, useContext, useState } from 'react';

export interface UserSession {
  readonly id: string;
  readonly name: string;
  readonly role: 'CASHIER' | 'BARISTA' | 'SUPERVISOR' | 'ADMIN';
  readonly workstationId: string;
  readonly tenantSlug: string;
  readonly tenantName: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly capabilities: readonly string[];
}

const DEFAULT_SESSION: UserSession = {
  id: 'STF-01',
  name: 'Sarah Jenkins',
  role: 'SUPERVISOR',
  workstationId: 'WS-LND-01',
  tenantSlug: 'artisan-coffee',
  tenantName: 'Artisan Coffee Roasters',
  branchId: 'BR-LND-01',
  branchName: 'London SoHo Roastery',
  capabilities: ['CAFE_QSR', 'POS_COUNTER', 'KDS_BARISTA', 'FIN_CORE', 'HR_CORE'],
};

interface AuthContextValue {
  readonly session: UserSession;
  readonly hasCapability: (cap: string) => boolean;
  readonly switchRole: (role: UserSession['role']) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { readonly children: React.ReactNode }): React.JSX.Element {
  const [session, setSession] = useState<UserSession>(DEFAULT_SESSION);

  const hasCapability = (cap: string): boolean => {
    return session.capabilities.includes(cap);
  };

  const switchRole = (role: UserSession['role']) => {
    setSession((prev) => ({ ...prev, role }));
  };

  return (
    <AuthContext.Provider value={{ session, hasCapability, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
