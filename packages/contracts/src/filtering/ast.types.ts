/**
 * AST Filtering types for zero-query-string allowlisted table filters.
 */
export type FilterOperator =
  | 'EQ'
  | 'NEQ'
  | 'GT'
  | 'GTE'
  | 'LT'
  | 'LTE'
  | 'IN'
  | 'CONTAINS'
  | 'BETWEEN';

export interface FilterPredicate {
  readonly field: string;
  readonly op: FilterOperator;
  readonly value: string | number | boolean | readonly (string | number)[];
}

export interface FilterGroup {
  readonly conjunction: 'AND' | 'OR';
  readonly predicates: readonly (FilterPredicate | FilterGroup)[];
}

export interface SavedFilterPresetDTO {
  readonly id: string;
  readonly name: string;
  readonly entity: string;
  readonly filter_group: FilterGroup;
  readonly is_default: boolean;
  readonly created_at: string;
}
