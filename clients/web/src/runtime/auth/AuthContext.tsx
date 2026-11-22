'use client';

import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';

export interface StaffProfile {
  readonly id: string;
  readonly name: string;
  readonly role: 'SUPERVISOR' | 'BARISTA' | 'CASHIER' | 'ADMIN';
  readonly pin: string;
  readonly avatarIcon: string;
  readonly title: string;
  readonly workstationId: string;
  readonly tenantSlug: string;
  readonly tenantName: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly capabilities: readonly string[];
}

export const PRECONFIGURED_STAFF: readonly StaffProfile[] = [
  {
    id: 'STF-01',
    name: 'Sarah Jenkins',
    role: 'SUPERVISOR',
    pin: '9999',
    avatarIcon: '☕',
    title: 'Head Barista & Supervisor',
    workstationId: 'WS-LND-01',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'KDS_BARISTA', 'FIN_CORE', 'HR_CORE'],
  },
  {
    id: 'STF-02',
    name: 'Marcus Vance',
    role: 'BARISTA',
    pin: '1234',
    avatarIcon: '🍳',
    title: 'Sous Chef & Kitchen Lead',
    workstationId: 'WS-KDS-02',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'KDS_BARISTA'],
  },
  {
    id: 'STF-03',
    name: 'Chloe Bennett',
    role: 'CASHIER',
    pin: '1111',
    avatarIcon: '🥐',
    title: 'Front Counter Cashier',
    workstationId: 'WS-POS-03',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'FIN_CORE'],
  },
  {
    id: 'STF-04',
    name: 'David Chen',
    role: 'ADMIN',
    pin: '0000',
    avatarIcon: '👔',
    title: 'General Manager & Admin',
    workstationId: 'WS-MGR-01',
    tenantSlug: 'artisan-coffee',
    tenantName: 'Artisan Coffee Roasters',
    branchId: 'BR-LND-01',
    branchName: 'London SoHo Roastery',
    capabilities: ['CAFE_QSR', 'POS_COUNTER', 'KDS_BARISTA', 'FIN_CORE', 'HR_CORE'],
  },
];

export interface UserSession {
  readonly id: string;
  readonly name: string;
  readonly role: 'SUPERVISOR' | 'BARISTA' | 'CASHIER' | 'ADMIN';
  readonly workstationId: string;
  readonly tenantSlug: string;
  readonly tenantName: string;
  readonly branchId: string;
  readonly branchName: string;
  readonly capabilities: readonly string[];
}

interface AuthContextValue {
  readonly session: UserSession;
  readonly isAuthenticated: boolean;
  readonly activeStaff: StaffProfile;
  readonly hasCapability: (cap: string) => boolean;
  readonly loginWithPin: (pin: string) => boolean;
  readonly selectStaff: (staffId: string) => void;
  readonly lockWorkstation: () => void;
  readonly switchRole: (role: UserSession['role']) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { readonly children: React.ReactNode }): React.JSX.Element {
  const [selectedStaff, setSelectedStaff] = useState<StaffProfile>(PRECONFIGURED_STAFF[0]);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  const session = useMemo<UserSession>(() => {
    return {
      id: selectedStaff.id,
      name: selectedStaff.name,
      role: selectedStaff.role,
      workstationId: selectedStaff.workstationId,
      tenantSlug: selectedStaff.tenantSlug,
      tenantName: selectedStaff.tenantName,
      branchId: selectedStaff.branchId,
      branchName: selectedStaff.branchName,
      capabilities: selectedStaff.capabilities,
    };
  }, [selectedStaff]);

  const hasCapability = useCallback((cap: string): boolean => {
    return session.capabilities.includes(cap);
  }, [session.capabilities]);

  const loginWithPin = useCallback((enteredPin: string): boolean => {
    // If entered PIN matches currently selected staff, or any staff
    if (selectedStaff.pin === enteredPin) {
      setIsAuthenticated(true);
      return true;
    }
    const matched = PRECONFIGURED_STAFF.find((s) => s.pin === enteredPin);
    if (matched) {
      setSelectedStaff(matched);
      setIsAuthenticated(true);
      return true;
    }
    return false;
  }, [selectedStaff]);

  const selectStaff = useCallback((staffId: string): void => {
    const found = PRECONFIGURED_STAFF.find((s) => s.id === staffId);
    if (found) {
      setSelectedStaff(found);
    }
  }, []);

  const lockWorkstation = useCallback((): void => {
    setIsAuthenticated(false);
  }, []);

  const switchRole = useCallback((role: UserSession['role']): void => {
    setSelectedStaff((prev) => ({ ...prev, role }));
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    session,
    isAuthenticated,
    activeStaff: selectedStaff,
    hasCapability,
    loginWithPin,
    selectStaff,
    lockWorkstation,
    switchRole,
  }), [session, isAuthenticated, selectedStaff, hasCapability, loginWithPin, selectStaff, lockWorkstation, switchRole]);

  return (
    <AuthContext.Provider value={value}>
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
