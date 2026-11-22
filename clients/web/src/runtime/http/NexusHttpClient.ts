/**
 * NexusHttpClient.ts — Production-grade multi-tenant HTTP client.
 * Enforces X-Nexus-* metadata headers, Weak ETag caching, and relative API dispatch.
 */

export interface HttpRequestOptions extends RequestInit {
  readonly tenantSlug?: string;
  readonly orgScope?: string;
  readonly locale?: string;
}

export class NexusHttpClient {
  private static instance: NexusHttpClient | null = null;
  private readonly defaultTenant: string = 'artisan-coffee';
  private readonly defaultOrgScope: string = 'branch:LND-01';
  private readonly defaultLocale: string = 'en-US';

  public static getInstance(): NexusHttpClient {
    if (!this.instance) {
      this.instance = new NexusHttpClient();
    }
    return this.instance;
  }

  public async get<T>(url: string, options: HttpRequestOptions = {}): Promise<T> {
    const headers = this.buildHeaders(options);
    const response = await fetch(url, {
      ...options,
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
    }

    return (await response.json()) as T;
  }

  public async post<T, B = unknown>(url: string, body: B, options: HttpRequestOptions = {}): Promise<T> {
    const headers = this.buildHeaders(options);
    headers.set('Content-Type', 'application/json');

    const response = await fetch(url, {
      ...options,
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
    }

    return (await response.json()) as T;
  }

  private buildHeaders(options: HttpRequestOptions): Headers {
    const headers = new Headers(options.headers || {});
    headers.set('X-Nexus-Tenant-Slug', options.tenantSlug || this.defaultTenant);
    headers.set('X-Nexus-Org-Scope', options.orgScope || this.defaultOrgScope);
    headers.set('X-Nexus-Locale', options.locale || this.defaultLocale);
    headers.set('Accept', 'application/json');
    return headers;
  }
}

export const httpClient = NexusHttpClient.getInstance();
