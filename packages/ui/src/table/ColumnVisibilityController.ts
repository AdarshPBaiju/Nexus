export class ColumnVisibilityController {
  private hiddenColumns = new Set<string>();
  private readonly listeners = new Set<() => void>();

  public get visibleColumns(): readonly string[] {
    return Array.from(this.hiddenColumns);
  }

  public mount(): void {}

  public dispose(): void {
    this.listeners.clear();
    this.hiddenColumns.clear();
  }

  public hideColumn(columnId: string): void {
    this.hiddenColumns.add(columnId);
    this.notify();
  }

  public showColumn(columnId: string): void {
    this.hiddenColumns.delete(columnId);
    this.notify();
  }

  public isColumnVisible(columnId: string): boolean {
    return !this.hiddenColumns.has(columnId);
  }

  public toggleColumn(columnId: string): void {
    if (this.hiddenColumns.has(columnId)) {
      this.hiddenColumns.delete(columnId);
    } else {
      this.hiddenColumns.add(columnId);
    }
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
