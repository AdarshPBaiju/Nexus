/**
 * NexusHeaders - Single Source of Truth for HTTP Header Constants across Project Nexus.
 */
export const NexusHeaders = {
  TENANT_SLUG: 'X-Nexus-Tenant-Slug',
  ORG_SCOPE: 'X-Nexus-Org-Scope',
  LOCALE: 'X-Nexus-Locale',
  I18N_ETAG: 'X-Nexus-I18n-ETag',
  IDEMPOTENCY_KEY: 'Idempotency-Key',
  IF_MATCH: 'If-Match',
  RYOW_TOKEN: 'X-Nexus-RYOW-Token',
  RUNTIME_SURFACE: 'X-Nexus-Runtime-Surface',
  REQUEST_ID: 'X-Nexus-Request-ID',
  CLIENT_VERSION: 'X-Nexus-Client-Version',
} as const;

export type NexusHeaderKey = (typeof NexusHeaders)[keyof typeof NexusHeaders];
