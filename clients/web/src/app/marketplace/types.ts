export type ExecutionSurface = 'WEB_ALL' | 'DESKTOP_ONLY' | 'HYBRID_WEB_DESKTOP';
export type PluginStatus = 'ACTIVE' | 'DRAINING' | 'ARCHIVED';

export interface PluginPackage {
  readonly code: string;
  readonly name: string;
  readonly description: string;
  readonly tier: string;
  readonly execution_surface: ExecutionSurface;
  readonly version: string;
  readonly status: PluginStatus;
  readonly icon: string;
  readonly category: string;
  readonly dependencies: readonly string[];
  readonly installed_at: number | null;
}
