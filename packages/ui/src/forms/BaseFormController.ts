import { FormValidationController } from './FormValidationController';
import { BatchLookupCoordinator } from './BatchLookupCoordinator';

export interface BaseFormOptions<TValues extends Record<string, unknown>> {
  readonly initialValues: TValues;
  readonly lookupCoordinator?: BatchLookupCoordinator;
}

export abstract class BaseFormController<TValues extends Record<string, unknown>> {
  protected values: TValues;
  protected readonly initialSnapshot: TValues;
  protected readonly validationController: FormValidationController;
  protected readonly lookupCoordinator: BatchLookupCoordinator;
  protected isSubmittingState: boolean = false;
  private readonly listeners = new Set<() => void>();

  protected constructor(options: BaseFormOptions<TValues>) {
    this.values = { ...options.initialValues };
    this.initialSnapshot = { ...options.initialValues };
    this.validationController = new FormValidationController();
    this.lookupCoordinator = options.lookupCoordinator || new BatchLookupCoordinator();
  }

  public get formValues(): Readonly<TValues> {
    return this.values;
  }

  public get isDirty(): boolean {
    return JSON.stringify(this.values) !== JSON.stringify(this.initialSnapshot);
  }

  public get isSubmitting(): boolean {
    return this.isSubmittingState;
  }

  public get validation(): FormValidationController {
    return this.validationController;
  }

  public get lookups(): BatchLookupCoordinator {
    return this.lookupCoordinator;
  }

  public setFieldValue<K extends keyof TValues>(field: K, value: TValues[K]): void {
    this.values = { ...this.values, [field]: value };
    this.validationController.clearError(field as string);
    this.notify();
  }

  public reset(): void {
    this.values = { ...this.initialSnapshot };
    this.validationController.reset();
    this.notify();
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  protected notify(): void {
    for (const l of this.listeners) {
      l();
    }
  }

  public abstract submit(): Promise<void>;
}
