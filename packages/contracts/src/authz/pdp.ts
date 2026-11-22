/**
 * Multi-Dimensional Authorization & Policy Decision Point Contracts.
 */

export const AuthzDecisions = {
  ALLOW: 'ALLOW',
  DENY: 'DENY',
} as const;

export type AuthzDecision = (typeof AuthzDecisions)[keyof typeof AuthzDecisions];

export const FieldClassifications = {
  READ: 'READ',
  MASKED: 'MASKED',
  WRITE: 'WRITE',
  HIDDEN: 'HIDDEN',
} as const;

export type FieldClassification = (typeof FieldClassifications)[keyof typeof FieldClassifications];

export interface CompiledPolicyDto {
  readonly tenantId: string;
  readonly membershipId: string;
  readonly allowedPermissions: readonly string[];
  readonly deniedPermissions: readonly string[];
  readonly flsRules: Record<string, FieldClassification>;
  readonly rbacVersion: number;
}
