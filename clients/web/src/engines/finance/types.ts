/**
 * types.ts - Core domain models and DTOs for Finance & Shift Register Console.
 */

export type TreasuryAccountType = 'CASH_DRAWER' | 'BANK_ACCOUNT' | 'GATEWAY_CLEARING';
export type ShiftSessionStatus = 'OPEN' | 'CLOSED' | 'RECONCILED';

export interface TreasuryAccountDto {
  readonly id: string;
  readonly accountName: string;
  readonly accountCode: string;
  readonly accountType: TreasuryAccountType;
  readonly currentBalance: string;
  readonly currency: string;
  readonly isActive: boolean;
}

export interface ShiftRegisterSessionDto {
  readonly id: string;
  readonly workstationId: string;
  readonly cashierUserId: string;
  readonly treasuryAccountId: string;
  readonly openedAt: string;
  readonly closedAt?: string | null;
  readonly openingFloat: string;
  readonly systemCashTotal: string;
  readonly expectedCashTotal: string;
  readonly actualCashCount?: string | null;
  readonly varianceAmount?: string | null;
  readonly status: ShiftSessionStatus;
}

export interface QuickExpenseDto {
  readonly id: string;
  readonly shiftSessionId?: string | null;
  readonly amount: string;
  readonly currency: string;
  readonly reasonCode: string;
  readonly description: string;
}

export interface DenominationItem {
  readonly value: number;
  readonly label: string;
  count: number;
}
