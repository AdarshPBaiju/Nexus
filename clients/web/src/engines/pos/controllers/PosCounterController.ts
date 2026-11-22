/**
 * PosCounterController.ts - In-memory high-velocity POS Counter Cart & State Controller.
 */

import type { PosCartItem, PosCartSummary, PosHeldTab } from '../types';

export class PosCounterController {
  private items: PosCartItem[] = [];
  private cachedItems: readonly PosCartItem[] = Object.freeze([]);
  private heldTabs: Map<string, PosHeldTab> = new Map();
  private discountPercent: number = 0;
  private readonly taxRate: number = 0.10;
  private readonly listeners: Set<() => void> = new Set();
  private readonly supervisorPin: string = '9999';

  public static create(): PosCounterController {
    return new PosCounterController();
  }

  public get currentItems(): readonly PosCartItem[] {
    return this.cachedItems;
  }

  public get allHeldTabs(): readonly PosHeldTab[] {
    return Object.freeze(Array.from(this.heldTabs.values()));
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  public get summary(): PosCartSummary {
    let subtotalNum = 0;
    let count = 0;
    for (const item of this.items) {
      if (item.isVoided) continue;
      const unit = parseFloat(item.unitPrice) || 0;
      let mods = 0;
      for (const m of item.selectedModifiers) {
        mods += parseFloat(m.priceDelta) || 0;
      }
      subtotalNum += (unit + mods) * item.quantity;
      count += item.quantity;
    }
    const discountNum = subtotalNum * (this.discountPercent / 100);
    const taxableNum = Math.max(0, subtotalNum - discountNum);
    const taxNum = taxableNum * this.taxRate;
    const totalNum = taxableNum + taxNum;

    return {
      subtotal: subtotalNum.toFixed(2),
      discount: discountNum.toFixed(2),
      tax: taxNum.toFixed(2),
      total: totalNum.toFixed(2),
      itemCount: count,
    };
  }

  public addItem(item: Omit<PosCartItem, 'id'>): void {
    const existing = this.items.find((i) => i.skuCode === item.skuCode && !i.isVoided);
    if (existing) {
      existing.quantity += item.quantity;
    } else {
      this.items.push({ ...item, id: `line-${Date.now()}-${Math.random().toString(36).slice(2, 7)}` });
    }
    this.notify();
  }

  public updateQuantity(itemId: string, delta: number): void {
    const target = this.items.find((i) => i.id === itemId);
    if (!target) return;
    target.quantity += delta;
    if (target.quantity <= 0) {
      this.items = this.items.filter((i) => i.id !== itemId);
    }
    this.notify();
  }

  public voidItem(itemId: string, managerPin: string): boolean {
    if (!this.verifySupervisorPin(managerPin)) return false;
    const target = this.items.find((i) => i.id === itemId);
    if (!target) return false;
    target.quantity = 0;
    this.items = this.items.filter((i) => i.id !== itemId);
    this.notify();
    return true;
  }

  public applyDiscount(percent: number, managerPin?: string): boolean {
    if (percent > 15 && (!managerPin || !this.verifySupervisorPin(managerPin))) {
      return false;
    }
    this.discountPercent = Math.max(0, Math.min(100, percent));
    this.notify();
    return true;
  }

  public holdTab(label: string): string {
    const tabId = `tab-${Date.now()}`;
    this.heldTabs.set(tabId, {
      tabId,
      label,
      items: [...this.items],
      heldAt: new Date().toLocaleTimeString(),
    });
    this.items = [];
    this.discountPercent = 0;
    this.notify();
    return tabId;
  }

  public resumeTab(tabId: string): boolean {
    const tab = this.heldTabs.get(tabId);
    if (!tab) return false;
    this.items = [...tab.items];
    this.heldTabs.delete(tabId);
    this.notify();
    return true;
  }

  public clearCart(): void {
    this.items = [];
    this.discountPercent = 0;
    this.notify();
  }

  public verifySupervisorPin(pin: string): boolean {
    return pin.trim() === this.supervisorPin;
  }

  private notify(): void {
    this.cachedItems = Object.freeze([...this.items]);
    this.listeners.forEach((l) => l());
  }
}
