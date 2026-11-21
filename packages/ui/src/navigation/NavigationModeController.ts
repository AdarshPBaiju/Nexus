import { NavigationMode } from './types';

export class NavigationModeController {
  private currentMode: NavigationMode = 'NESTED_SIDEBAR';
  private isCollapsedState: boolean = false;
  private readonly listeners = new Set<() => void>();

  public get mode(): NavigationMode {
    return this.currentMode;
  }

  public get isCollapsed(): boolean {
    return this.isCollapsedState;
  }

  public setMode(newMode: NavigationMode): void {
    if (this.currentMode === newMode) return;
    this.currentMode = newMode;
    this.notify();
  }

  public toggleCollapse(): void {
    this.isCollapsedState = !this.isCollapsedState;
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
