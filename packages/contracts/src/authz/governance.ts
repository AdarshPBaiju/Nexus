/**
 * Segregation of Duties (SoD), JIT Elevation & Step-Up Auth Contracts.
 */

export interface SodViolationDto {
  readonly ruleCode: string;
  readonly firstPermission: string;
  readonly conflictingPermission: string;
  readonly message: string;
}

export interface StepUpTicketDto {
  readonly token: string;
  readonly supervisorId: string;
  readonly targetAction: string;
  readonly expiresAt: string;
}

export interface JitElevationRequestDto {
  readonly targetRole: string;
  readonly durationMinutes: number;
  readonly justification: string;
}
