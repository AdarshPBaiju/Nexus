'use client';
import React, { createContext, useContext, useMemo } from 'react';

export type SurfaceRole =
  | 'canvas'
  | 'card'
  | 'subtle'
  | 'elevated'
  | 'primary-action'
  | 'destructive-action'
  | 'tooltip'
  | 'status-success-subtle'
  | 'status-warning-subtle'
  | 'status-danger-subtle'
  | 'status-info-subtle'
  | 'selected';

const SurfaceContext = createContext<SurfaceRole>('canvas');

export interface SurfaceProviderProps {
  readonly role: SurfaceRole;
  readonly children: React.ReactNode;
}

export function SurfaceProvider({ role, children }: SurfaceProviderProps): React.JSX.Element {
  const value = useMemo(() => role, [role]);
  return <SurfaceContext.Provider value={value}>{children}</SurfaceContext.Provider>;
}

export function useSurface(): SurfaceRole {
  return useContext(SurfaceContext);
}
