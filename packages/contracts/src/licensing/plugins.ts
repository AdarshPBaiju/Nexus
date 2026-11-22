/**
 * ExecutionSurface & Plugin Licensing Contracts for Project Nexus.
 */

export const ExecutionSurfaces = {
  WEB_ALL: 'WEB_ALL',
  DESKTOP_ONLY: 'DESKTOP_ONLY',
  HYBRID_WEB_DESKTOP: 'HYBRID_WEB_DESKTOP',
} as const;

export type ExecutionSurface = (typeof ExecutionSurfaces)[keyof typeof ExecutionSurfaces];

export interface ModulePackageDto {
  readonly id: string;
  readonly code: string;
  readonly name: string;
  readonly executionSurface: ExecutionSurface;
  readonly isActive: boolean;
}

export interface DesktopHandoffParams {
  readonly tenantSlug: string;
  readonly route: string;
  readonly stationId?: string;
}

/**
 * Builds standard 1-click nexus:// desktop handoff URI for <DesktopRuntimeGuard>.
 */
export function buildDesktopHandoffUri(params: DesktopHandoffParams): string {
  const query = new URLSearchParams({
    tenant: params.tenantSlug,
    route: params.route,
  });
  if (params.stationId) {
    query.set('station', params.stationId);
  }
  return `nexus://open?${query.toString()}`;
}
