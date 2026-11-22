/**
 * WorkspaceCacheRegistry - Single Source of Truth for In-Memory Cache Isolation.
 * Enforces atomic memory purging across all caches when switching tenants or logging out.
 */

export interface CacheFlusher {
  clear(): void | Promise<void>;
}

export class WorkspaceCacheRegistry {
  private static readonly flushers = new Set<CacheFlusher>();

  public static register(flusher: CacheFlusher): () => void {
    this.flushers.add(flusher);
    return () => {
      this.flushers.delete(flusher);
    };
  }

  public static async purgeAll(): Promise<void> {
    const promises: Promise<void>[] = [];
    for (const flusher of this.flushers) {
      try {
        const res = flusher.clear();
        if (res instanceof Promise) {
          promises.push(res);
        }
      } catch {
        // Fail-safe: continue clearing other caches
      }
    }
    await Promise.all(promises);
  }

  public static get size(): number {
    return this.flushers.size;
  }
}
