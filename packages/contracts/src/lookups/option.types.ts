/**
 * Option items and batch lookup DTO contracts.
 */
export interface OptionItemDTO<T = string> {
  readonly value: T;
  readonly label: string;
  readonly is_active: boolean;
  readonly icon?: string;
  readonly group?: string;
  readonly metadata?: Record<string, unknown>;
}

export interface BatchLookupRequest {
  readonly queries: readonly {
    readonly key: string;
    readonly entity: string;
    readonly search?: string;
    readonly parent_id?: string;
  }[];
}

export interface BatchLookupResponse {
  readonly results: Record<string, readonly OptionItemDTO[]>;
}
