/**
 * Multilingual Core Contracts & Backend Translation Engine Types.
 */

export interface LocaleDefinitionDto {
  readonly code: string;
  readonly baseLanguage: string;
  readonly nativeName: string;
  readonly textDirection: 'ltr' | 'rtl';
  readonly isPlatformSource: boolean;
}

export interface CompiledBundleDto {
  readonly namespace: string;
  readonly locale: string;
  readonly etag: string;
  readonly messages: Record<string, string>;
  readonly compiledAt: string;
}

export interface I18nBundlePublishedEventDto {
  readonly specversion: '1.0';
  readonly id: string;
  readonly type: 'i18n.bundle.published.v1';
  readonly source: string;
  readonly data: {
    readonly namespace: string;
    readonly locale: string;
    readonly tenantId: string;
    readonly etag: string;
  };
}

export function isWeakEtagMatch(clientEtag: string | null, serverEtag: string): boolean {
  if (!clientEtag) return false;
  const cleanClient = clientEtag.trim();
  const cleanServer = serverEtag.trim();
  return cleanClient === cleanServer || cleanClient === `W/"${cleanServer.replace(/^W\/"|"$/g, '')}"`;
}
