/**
 * Exact string-decimal ISO 4217 Money value object.
 * Guarantees zero floating-point precision loss.
 */
export class Money {
  private static readonly SCALE = 4;
  private static readonly MULTIPLIER = 10000n;

  public readonly amount: string;
  public readonly currency: string;
  private readonly rawUnits: bigint;

  public constructor(amount: string, currency: string) {
    if (!currency || currency.length !== 3) {
      throw new Error(`Invalid ISO 4217 currency code: ${currency}`);
    }
    this.currency = currency.toUpperCase();
    this.rawUnits = Money.parseToRawUnits(amount);
    this.amount = Money.rawUnitsToString(this.rawUnits);
  }

  public static of(amount: string | number, currency: string): Money {
    return new Money(typeof amount === 'number' ? amount.toFixed(4) : amount, currency);
  }

  public static zero(currency: string): Money {
    return new Money('0.0000', currency);
  }

  public add(other: Money): Money {
    this.assertSameCurrency(other);
    return Money.fromRawUnits(this.rawUnits + other.rawUnits, this.currency);
  }

  public subtract(other: Money): Money {
    this.assertSameCurrency(other);
    return Money.fromRawUnits(this.rawUnits - other.rawUnits, this.currency);
  }

  public multiply(factor: number | string): Money {
    const factorScaled = BigInt(Math.round(Number(factor) * 10000));
    const resultRaw = (this.rawUnits * factorScaled) / Money.MULTIPLIER;
    return Money.fromRawUnits(resultRaw, this.currency);
  }

  public divide(divisor: number | string): Money {
    const numDivisor = Number(divisor);
    if (numDivisor === 0) {
      throw new Error('Division by zero in Money.divide');
    }
    const divisorScaled = BigInt(Math.round(numDivisor * 10000));
    const resultRaw = (this.rawUnits * Money.MULTIPLIER) / divisorScaled;
    return Money.fromRawUnits(resultRaw, this.currency);
  }

  public allocate(ratios: number[]): Money[] {
    if (ratios.length === 0) return [];
    const totalRatio = ratios.reduce((sum, r) => sum + r, 0);
    if (totalRatio <= 0) throw new Error('Allocation ratios sum must be positive');

    let remainder = this.rawUnits;
    const results: Money[] = [];

    for (let i = 0; i < ratios.length; i++) {
      const share = (this.rawUnits * BigInt(ratios[i])) / BigInt(totalRatio);
      results.push(Money.fromRawUnits(share, this.currency));
      remainder -= share;
    }

    // Distribute remaining sub-units one by one
    for (let i = 0; remainder > 0n && i < results.length; i++) {
      results[i] = Money.fromRawUnits(results[i].rawUnits + 1n, this.currency);
      remainder -= 1n;
    }
    return results;
  }

  public isEqual(other: Money): boolean {
    return this.currency === other.currency && this.rawUnits === other.rawUnits;
  }

  public isGreaterThan(other: Money): boolean {
    this.assertSameCurrency(other);
    return this.rawUnits > other.rawUnits;
  }

  public isLessThan(other: Money): boolean {
    this.assertSameCurrency(other);
    return this.rawUnits < other.rawUnits;
  }

  public isZero(): boolean {
    return this.rawUnits === 0n;
  }

  public isNegative(): boolean {
    return this.rawUnits < 0n;
  }

  private assertSameCurrency(other: Money): void {
    if (this.currency !== other.currency) {
      throw new Error(`Currency mismatch: ${this.currency} !== ${other.currency}`);
    }
  }

  private static parseToRawUnits(amountStr: string): bigint {
    const cleaned = amountStr.trim();
    const isNeg = cleaned.startsWith('-');
    const absStr = isNeg ? cleaned.slice(1) : cleaned;
    const parts = absStr.split('.');
    const integerPart = BigInt(parts[0] || '0');
    const fracStr = (parts[1] || '').padEnd(Money.SCALE, '0').slice(0, Money.SCALE);
    const fractionalPart = BigInt(fracStr);
    const total = integerPart * Money.MULTIPLIER + fractionalPart;
    return isNeg ? -total : total;
  }

  private static rawUnitsToString(raw: bigint): string {
    const isNeg = raw < 0n;
    const abs = isNeg ? -raw : raw;
    const intPart = (abs / Money.MULTIPLIER).toString();
    const fracPart = (abs % Money.MULTIPLIER).toString().padStart(Money.SCALE, '0');
    const result = `${intPart}.${fracPart}`;
    return isNeg ? `-${result}` : result;
  }

  private static fromRawUnits(rawUnits: bigint, currency: string): Money {
    const instance = Object.create(Money.prototype);
    Object.assign(instance, {
      currency,
      rawUnits,
      amount: Money.rawUnitsToString(rawUnits),
    });
    return Object.freeze(instance);
  }
}
