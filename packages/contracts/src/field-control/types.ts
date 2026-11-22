/**
 * Type-safe ask-only field projection utilities for Project Nexus.
 */

export type ProjectedDto<T, K extends keyof T> = Pick<T, K>;

export interface FieldProjectionRequest<T> {
  readonly selectedFields: ReadonlyArray<keyof T>;
}
