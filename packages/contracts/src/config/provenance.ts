/**
 * 9-Field Provenance & 6-Level Dynamic Config TypeScript Contracts.
 */

export const ScopeLevels = {
  PLATFORM: 'PLATFORM',
  TENANT: 'TENANT',
  BRAND: 'BRAND',
  BRANCH: 'BRANCH',
  ZONE: 'ZONE',
  WORKSTATION: 'WORKSTATION',
} as const;

export type ScopeLevel = (typeof ScopeLevels)[keyof typeof ScopeLevels];

export const LockStatuses = {
  UNLOCKED: 'UNLOCKED',
  LOCKED_BY_PARENT: 'LOCKED_BY_PARENT',
  STATUTORY_GUARDRAIL: 'STATUTORY_GUARDRAIL',
} as const;

export type LockStatus = (typeof LockStatuses)[keyof typeof LockStatuses];

export interface ProvenanceRecordDto<T = unknown> {
  readonly effectiveValue: T;
  readonly sourceLevel: ScopeLevel;
  readonly sourceRevisionId: string;
  readonly inheritanceChain: readonly ScopeLevel[];
  readonly overrideHistoryRef: string;
  readonly lockStatus: LockStatus;
  readonly validationStatus: 'VALID' | 'WARNING' | 'INVALID';
  readonly resolvedAt: string;
  readonly applicablePluginVersion: string;
}
