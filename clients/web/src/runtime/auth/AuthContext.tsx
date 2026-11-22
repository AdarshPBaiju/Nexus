'use client';

import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { WorkspaceCacheRegistry } from '@nexus/contracts';
import {
  PRECONFIGURED_STAFF,
  PRECONFIGURED_TENANTS,
  type AuthContextValue,
  type StaffProfile,
  type TenantWorkspace,
  type UserSession,
} from './authTypes';

export * from './authTypes';

const STAFF_STORAGE_KEY = 'nexus.auth.staffId';
const SESSION_STORAGE_KEY = 'nexus.auth.active';
const TENANT_STORAGE_KEY = 'nexus.auth.tenantSlug';

const AuthContext = createContext<AuthContextValue | null>(null);

async function hashPin(pin: string): Promise<string> {
  const bytes = new TextEncoder().encode(pin);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}

export function AuthProvider({ children }: { readonly children: React.ReactNode }): React.JSX.Element {
  const [tenants, setTenants] = useState<readonly TenantWorkspace[]>(PRECONFIGURED_TENANTS);
  const [activeTenant, setActiveTenant] = useState<TenantWorkspace>(PRECONFIGURED_TENANTS[0]);
  const [selectedStaff, setSelectedStaff] = useState<StaffProfile>(PRECONFIGURED_STAFF[0]);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isHydrated, setIsHydrated] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const storedStaffId = window.sessionStorage.getItem(STAFF_STORAGE_KEY);
      const storedTenantSlug = window.sessionStorage.getItem(TENANT_STORAGE_KEY);
      const isActive = window.sessionStorage.getItem(SESSION_STORAGE_KEY) === '1';

      if (storedTenantSlug) {
        const matchedTenant = PRECONFIGURED_TENANTS.find((t) => t.slug === storedTenantSlug);
        if (matchedTenant) setActiveTenant(matchedTenant);
      }
      if (storedStaffId) {
        const matched = PRECONFIGURED_STAFF.find((s) => s.id === storedStaffId);
        if (matched) setSelectedStaff(matched);
      }
      setIsAuthenticated(isActive);
    } catch {
      // Memory fallback in hardened environments.
    }
    setIsHydrated(true);
  }, []);

  const switchTenant = useCallback((slug: string): void => {
    const target = tenants.find((t) => t.slug === slug);
    if (!target) return;

    // Purge memory cache to guarantee zero cross-tenant leakage.
    WorkspaceCacheRegistry.purgeAll();

    setActiveTenant(target);
    setSelectedStaff((prev) => ({
      ...prev,
      tenantSlug: target.slug,
      tenantName: target.name,
      branchId: target.branchId,
      branchName: target.branchName,
    }));

    try {
      window.sessionStorage.setItem(TENANT_STORAGE_KEY, target.slug);
    } catch {
      // Memory-only fallback.
    }
  }, [tenants]);

  const registerTenantWorkspace = useCallback((workspace: TenantWorkspace): void => {
    setTenants((prev) => (prev.some((t) => t.slug === workspace.slug) ? prev : [...prev, workspace]));
    switchTenant(workspace.slug);
  }, [switchTenant]);

  const session = useMemo<UserSession>(() => ({
    id: selectedStaff.id,
    name: selectedStaff.name,
    role: selectedStaff.role,
    workstationId: selectedStaff.workstationId,
    tenantSlug: activeTenant.slug,
    tenantName: activeTenant.name,
    branchId: activeTenant.branchId,
    branchName: activeTenant.branchName,
    capabilities: selectedStaff.capabilities,
  }), [selectedStaff, activeTenant]);

  const hasCapability = useCallback((cap: string): boolean => session.capabilities.includes(cap), [session.capabilities]);

  const loginWithPin = useCallback(async (enteredPin: string): Promise<boolean> => {
    const enteredHash = await hashPin(enteredPin);
    const matched = PRECONFIGURED_STAFF.find((staff) => staff.pinHash === enteredHash);
    if (!matched) return false;
    setSelectedStaff(matched);
    setIsAuthenticated(true);
    return true;
  }, []);

  const selectStaff = useCallback((staffId: string): void => {
    const found = PRECONFIGURED_STAFF.find((s) => s.id === staffId);
    if (found) setSelectedStaff(found);
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
    availableTenants: tenants,
    activeTenant,
    hasCapability,
    loginWithPin,
    selectStaff,
    lockWorkstation,
    switchRole,
    switchTenant,
    registerTenantWorkspace,
  }), [session, isAuthenticated, isHydrated, selectedStaff, tenants, activeTenant, hasCapability, loginWithPin, selectStaff, lockWorkstation, switchRole, switchTenant, registerTenantWorkspace]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
