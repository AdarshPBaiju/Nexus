import { ColumnVisibilityController } from './ColumnVisibilityController';
import { TablePaginationController } from './TablePaginationController';

export interface BaseListingOptions {
  readonly tenantSlug: string;
  readonly defaultPageSize?: number;
}

export abstract class BaseListingController<TRow> {
  public static readonly DEFAULT_PAGE_SIZE = 25;

  protected readonly tenantSlug: string;
  protected readonly visibilityController: ColumnVisibilityController;
  protected readonly paginationController: TablePaginationController;
  protected rows: readonly TRow[] = [];
  protected isBusy: boolean = false;
  private readonly subscribers = new Set<() => void>();

  protected constructor(options: BaseListingOptions) {
    this.tenantSlug = options.tenantSlug;
    this.visibilityController = new ColumnVisibilityController();
    this.paginationController = new TablePaginationController({
      pageSize: options.defaultPageSize || BaseListingController.DEFAULT_PAGE_SIZE,
    });
  }

  public get data(): readonly TRow[] {
    return this.rows;
  }

  public get loading(): boolean {
    return this.isBusy;
  }

  public get visibility(): ColumnVisibilityController {
    return this.visibilityController;
  }

  public get pagination(): TablePaginationController {
    return this.paginationController;
  }

  public mount(): void {
    this.visibilityController.mount();
  }

  public dispose(): void {
    this.subscribers.clear();
    this.visibilityController.dispose();
  }

  public subscribe(callback: () => void): () => void {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  protected emitChange(): void {
    for (const callback of this.subscribers) {
      callback();
    }
  }

  public abstract loadRows(): Promise<void>;
}
