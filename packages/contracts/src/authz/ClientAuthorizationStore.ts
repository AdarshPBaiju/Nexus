/**
 * Client-Side Authorization Reactive Store.
 * Evaluates permissions and FLS rules in-memory with sub-millisecond latency.
 */

import type { CompiledPolicyDto, FieldClassification } from './pdp';

export type PolicyChangeListener = (policy: CompiledPolicyDto | null) => void;

export class ClientAuthorizationStore {
  private static instance: ClientAuthorizationStore | null = null;
  private currentPolicy: CompiledPolicyDto | null = null;
  private readonly listeners: Set<PolicyChangeListener> = new Set();

  public static getInstance(): ClientAuthorizationStore {
    if (!ClientAuthorizationStore.instance) {
      ClientAuthorizationStore.instance = new ClientAuthorizationStore();
    }
    return ClientAuthorizationStore.instance;
  }

  public setPolicy(policy: CompiledPolicyDto): void {
    this.currentPolicy = Object.freeze({ ...policy });
    this.notifyListeners();
  }

  public clearPolicy(): void {
    this.currentPolicy = null;
    this.notifyListeners();
  }

  public can(permission: string): boolean {
    if (!this.currentPolicy) return false;
    if (this.currentPolicy.deniedPermissions.includes(permission)) return false;
    return this.currentPolicy.allowedPermissions.includes(permission);
  }

  public getFieldClassification(entityType: string, fieldName: string): FieldClassification {
    if (!this.currentPolicy) return 'READ';
    const key = `${entityType}:${fieldName}`;
    return this.currentPolicy.flsRules[key] || 'READ';
  }

  public subscribe(listener: PolicyChangeListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(): void {
    for (const listener of this.listeners) {
      listener(this.currentPolicy);
    }
  }
}
