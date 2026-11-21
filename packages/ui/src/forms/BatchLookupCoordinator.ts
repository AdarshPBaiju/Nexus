import { OptionItemDTO } from '@nexus/contracts';

export interface QueuedQuery {
  readonly key: string;
  readonly entity: string;
}

export class BatchLookupCoordinator {
  private queue: QueuedQuery[] = [];
  private cache = new Map<string, readonly OptionItemDTO[]>();
  private scheduledBatch: Promise<void> | null = null;

  public requestOptions(key: string, entity: string): readonly OptionItemDTO[] | null {
    const cached = this.cache.get(key);
    if (cached) return cached;

    if (!this.queue.some((q) => q.key === key)) {
      this.queue.push({ key, entity });
    }
    return null;
  }

  public setOptions(key: string, options: readonly OptionItemDTO[]): void {
    this.cache.set(key, options);
  }

  public getCachedOptions(key: string): readonly OptionItemDTO[] | undefined {
    return this.cache.get(key);
  }

  public clear(): void {
    this.queue = [];
    this.cache.clear();
  }
}
