export interface PaginationOptions {
  readonly pageSize: number;
}

export class TablePaginationController {
  private size: number;
  private currentCursor: string | null = null;
  private hasMoreRows: boolean = false;
  private readonly listeners = new Set<() => void>();

  public constructor(options: PaginationOptions) {
    this.size = options.pageSize;
  }

  public get pageSize(): number {
    return this.size;
  }

  public get cursor(): string | null {
    return this.currentCursor;
  }

  public get hasNext(): boolean {
    return this.hasMoreRows;
  }

  public setPageSize(newSize: number): void {
    if (newSize <= 0) return;
    this.size = newSize;
    this.notify();
  }

  public setCursor(cursor: string | null, hasNext: boolean): void {
    this.currentCursor = cursor;
    this.hasMoreRows = hasNext;
    this.notify();
  }

  public reset(): void {
    this.currentCursor = null;
    this.hasMoreRows = false;
    this.notify();
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const l of this.listeners) {
      l();
    }
  }
}
