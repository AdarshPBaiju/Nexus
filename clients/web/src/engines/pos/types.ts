/**
 * types.ts - Core domain models and DTOs for POS Counter Operations.
 */

export interface PosModifierOption {
  readonly id: string;
  readonly name: string;
  readonly priceDelta: string;
}

export interface PosCartItem {
  readonly id: string;
  readonly skuCode: string;
  readonly name: string;
  readonly unitPrice: string;
  quantity: number;
  readonly selectedModifiers: readonly PosModifierOption[];
  readonly isVoided?: boolean;
}

export interface SplitTenderEntry {
  readonly tenderType: 'CASH' | 'CARD' | 'DIGITAL_QR';
  amount: string;
  tenderedAmount: string;
  changeReturned: string;
}

export interface PosHeldTab {
  readonly tabId: string;
  readonly label: string;
  readonly items: readonly PosCartItem[];
  readonly heldAt: string;
}

export interface PosCartSummary {
  readonly subtotal: string;
  readonly discount: string;
  readonly tax: string;
  readonly total: string;
  readonly itemCount: number;
}
