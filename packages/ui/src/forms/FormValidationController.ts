export class FormValidationController {
  private errors = new Map<string, string>();
  private readonly listeners = new Set<() => void>();

  public get hasErrors(): boolean {
    return this.errors.size > 0;
  }

  public getFieldError(field: string): string | undefined {
    return this.errors.get(field);
  }

  public setFieldError(field: string, error: string): void {
    this.errors.set(field, error);
    this.notify();
  }

  public clearError(field: string): void {
    if (this.errors.delete(field)) {
      this.notify();
    }
  }

  public reset(): void {
    this.errors.clear();
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
