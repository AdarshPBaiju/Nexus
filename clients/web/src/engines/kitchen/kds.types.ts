/**
 * kds.types.ts - TypeScript contracts for Kitchen Display System (KDS).
 */

export type KdsStationType =
  | 'BARISTA'
  | 'HOT_KITCHEN'
  | 'BAKERY'
  | 'DESSERT'
  | 'EXPO';

export type KdsTicketStatus = 'NEW' | 'IN_PREP' | 'READY' | 'SERVED';

export interface KdsTicketLineDto {
  readonly id: string;
  readonly itemName: string;
  readonly quantity: number;
  readonly modifierNotes: readonly string[];
  readonly allergenFlags: readonly string[];
  readonly isCompleted: boolean;
}

export interface KdsTicketDto {
  readonly id: string;
  readonly orderToken: string;
  readonly stationType: KdsStationType;
  readonly status: KdsTicketStatus;
  readonly slaSeconds: number;
  readonly elapsedSeconds: number;
  readonly lines: readonly KdsTicketLineDto[];
  readonly diningType?: 'DINE_IN' | 'TAKEAWAY';
}
