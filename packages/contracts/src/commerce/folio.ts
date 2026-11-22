/**
 * Polymorphic Commerce Folio & Resource Scheduler Contracts.
 */

export const FolioStatuses = {
  OPEN: 'OPEN',
  LOCKED_FOR_PAYMENT: 'LOCKED_FOR_PAYMENT',
  SETTLED: 'SETTLED',
  CLOSED: 'CLOSED',
} as const;

export type FolioStatus = (typeof FolioStatuses)[keyof typeof FolioStatuses];

export interface FolioLineItemDto {
  readonly id: string;
  readonly itemType: string;
  readonly description: string;
  readonly quantity: string;
  readonly unitPrice: string;
  readonly taxAmount: string;
  readonly totalAmount: string;
}

export interface CommerceFolioDto {
  readonly id: string;
  readonly folioNumber: string;
  readonly branchId: string;
  readonly customerId: string | null;
  readonly status: FolioStatus;
  readonly version: number;
  readonly currency: string;
  readonly subtotalAmount: string;
  readonly taxAmount: string;
  readonly totalAmount: string;
  readonly lines: readonly FolioLineItemDto[];
}

export interface ResourceAllocationDto {
  readonly id: string;
  readonly resourceId: string;
  readonly folioId: string | null;
  readonly startTime: string;
  readonly endTime: string;
  readonly status: 'CONFIRMED' | 'ACTIVE' | 'HOLD_LOCKED' | 'RELEASED' | 'CANCELLED';
}
