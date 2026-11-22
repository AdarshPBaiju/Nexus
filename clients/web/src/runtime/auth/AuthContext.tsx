'use client';

import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';

const STAFF_STORAGE_KEY = 'nexus.auth.staffId';
const SESSION_STORAGE_KEY = 'nexus.auth.active';

export interface StaffProfile {
  readonly id: string;
  readonly name: string;
  readonly role: 'SUPERVISOR' | 'BARISTA' | 'CASHIER' | 'ADMIN';
  readonly pinHash: string;
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
    pinHash: '888df25ae35772424a560c7152a1de794440e0ea5cfee62828333a456a506e05',
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
    pinHash: '03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4',
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
    pinHash: '0ffe1abd1a08215353c233d6e009613e95eec4253832a761af28ff37ac5a150c',
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
    pinHash: '9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0',
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
  readonly isHydrated: boolean;
  readonly activeStaff: StaffProfile;
  readonly hasCapability: (cap: string) => boolean;
  readonly loginWithPin: (pin: string) => Promise<boolean>;
  readonly selectStaff: (staffId: string) => void;
  readonly lockWorkstation: () => void;
  readonly switchRole: (role: UserSession['role']) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

async function hashPin(pin: string): Promise<string> {
  const bytes = new TextEncoder().encode(pin);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

function readPersistedSession(): { readonly staffId: string | null; readonly active: boolean } {
  if (typeof window === 'undefined') {
    return { staffId: null, active: false };
  }
  try {
    return {
      staffId: window.sessionStorage.getItem(STAFF_STORAGE_KEY),
      active: window.sessionStorage.getItem(SESSION_STORAGE_KEY) === '1',
    };
  } catch {
    return { staffId: null, active: false };
  }
}

function persistSession(staffId: string, active: boolean): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.setItem(STAFF_STORAGE_KEY, staffId);
    if (active) {
      window.sessionStorage.setItem(SESSION_STORAGE_KEY, '1');
    } else {
      window.sessionStorage.removeItem(SESSION_STORAGE_KEY);
    }
  } catch {
    // Storage can be unavailable in hardened kiosk contexts; remain memory-only.
  }
}

export function AuthProvider({ children }: { readonly children: React.ReactNode }): React.JSX.Element {
  const [selectedStaff, setSelectedStaff] = useState<StaffProfile>(PRECONFIGURED_STAFF[0]);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  // Restore the terminal session after a refresh so the cashier stays signed in.
  useEffect(() => {
    const persisted = readPersistedSession();
    const restoredStaff = persisted.staffId
      ? PRECONFIGURED_STAFF.find((staff) => staff.id === persisted.staffId)
      : undefined;
    if (restoredStaff) {
      setSelectedStaff(restoredStaff);
    }
    setIsAuthenticated(persisted.active && Boolean(restoredStaff));
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (!isHydrated) return;
    persistSession(selectedStaff.id, isAuthenticated);
  }, [selectedStaff.id, isAuthenticated, isHydrated]);

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

  const loginWithPin = useCallback(async (enteredPin: string): Promise<boolean> => {
    const enteredHash = await hashPin(enteredPin);
    const matched = PRECONFIGURED_STAFF.find((staff) => staff.pinHash === enteredHash);
    if (!matched) {
      return false;
    }
    setSelectedStaff(matched);
    setIsAuthenticated(true);
    return true;
  }, []);

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
    isHydrated,
    activeStaff: selectedStaff,
    hasCapability,
    loginWithPin,
    selectStaff,
    lockWorkstation,
    switchRole,
  }), [session, isAuthenticated, isHydrated, selectedStaff, hasCapability, loginWithPin, selectStaff, lockWorkstation, switchRole]);

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
