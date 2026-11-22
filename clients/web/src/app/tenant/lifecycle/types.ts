export type TenantStatus = 'ACTIVE' | 'MAINTENANCE' | 'DRAINING' | 'SUSPENDED';

export interface AuditEvent {
  readonly id: string;
  readonly timestamp: number;
  readonly action: string;
  readonly actor: string;
  readonly detail: string;
}

export interface TenantLifecycleData {
  readonly tenant_id: string;
  readonly slug: string;
  readonly legal_name: string;
  readonly status: TenantStatus;
  readonly home_region: string;
  readonly kms_key_version: string;
  readonly uptime_seconds: number;
  readonly active_branches: number;
  readonly active_stations: number;
  readonly compliance_mode: string;
  readonly pci_dss_level: string;
  readonly audit_events: readonly AuditEvent[];
}
