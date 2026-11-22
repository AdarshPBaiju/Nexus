/**
 * ActorType & ActorContext - 5-Actor separation types for Project Nexus.
 */
export const ActorTypes = {
  STAFF: 'STAFF',
  PASSPORT_CONSUMER: 'PASSPORT_CONSUMER',
  DESKTOP_DEVICE: 'DESKTOP_DEVICE',
  API_KEY: 'API_KEY',
  OAUTH_APP: 'OAUTH_APP',
} as const;

export type ActorType = (typeof ActorTypes)[keyof typeof ActorTypes];

export interface ActorContextDto {
  readonly actorType: ActorType;
  readonly actorId: string;
  readonly tenantId?: string;
  readonly scopes: readonly string[];
  readonly isAuthenticated: boolean;
}
