/**
 * Execution surfaces, platforms, and desktop workstation binding contracts.
 */
export type ExecutionSurface = 'WEB_ALL' | 'DESKTOP_ONLY' | 'HYBRID_WEB_DESKTOP';

export type ClientPlatform =
  | 'web'
  | 'desktop_windows'
  | 'desktop_macos'
  | 'desktop_linux'
  | 'mobile_ios'
  | 'mobile_android';

export interface DesktopDeviceBinding {
  readonly workstation_uid: string;
  readonly os_platform: ClientPlatform;
  readonly desktop_app_version: string;
  readonly public_key_ed25519: string;
  readonly registered_at: string;
}
