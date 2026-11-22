/**
 * Polyglot Keyset Pagination & Fast Listing Contracts.
 */

export interface KeysetPageDto<T> {
  readonly items: readonly T[];
  readonly hasNext: boolean;
  readonly nextCursor: string | null;
  readonly prevCursor: string | null;
}

export interface FavouritesAnnotationDto {
  readonly isFavourite: boolean;
}

export function isListingWeakEtagMatch(clientEtag: string | null, serverEtag: string): boolean {
  if (!clientEtag) return false;
  const cleanClient = clientEtag.trim();
  const cleanServer = serverEtag.trim();
  return cleanClient === cleanServer || cleanClient === `W/"${cleanServer.replace(/^W\/"|"$/g, '')}"`;
}
