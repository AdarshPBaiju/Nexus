/**
 * catalog.types.ts - TypeScript contracts for Café QSR catalog, modifiers, combos, and tokens.
 */

export type PreparationStationType =
  | 'BARISTA'
  | 'HOT_KITCHEN'
  | 'BAKERY'
  | 'DESSERT'
  | 'COLD_BAR';

export interface ModifierOptionDto {
  readonly id: string;
  readonly name: string;
  readonly priceDelta: string;
  readonly isDefault?: boolean;
}

export interface ModifierGroupDto {
  readonly id: string;
  readonly name: string;
  readonly minSelection: number;
  readonly maxSelection: number;
  readonly isRequired: boolean;
  readonly options: readonly ModifierOptionDto[];
}

export interface MenuItemDto {
  readonly id: string;
  readonly categoryId: string;
  readonly skuCode: string;
  readonly name: string;
  readonly basePrice: string;
  readonly currency: string;
  readonly taxRatePercent: string;
  readonly preparationStation: PreparationStationType;
  readonly imageUrl?: string;
  readonly modifierGroups?: readonly ModifierGroupDto[];
}

export interface MenuCategoryDto {
  readonly id: string;
  readonly name: string;
  readonly slug: string;
  readonly sortOrder: number;
  readonly isActive: boolean;
}

export interface ComboRuleDto {
  readonly id: string;
  readonly name: string;
  readonly bundlePrice: string;
  readonly currency: string;
  readonly requiredCategoryIds: readonly string[];
}

export interface OrderPickupTokenDto {
  readonly token: string;
  readonly orderNumber: string;
  readonly status: 'PREPARING' | 'READY' | 'COLLECTED';
  readonly station: PreparationStationType;
  readonly updatedAt: string;
}
