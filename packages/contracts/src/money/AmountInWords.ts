/**
 * packages/contracts/src/money/AmountInWords.ts
 *
 * Universal Multilingual Amount-in-Words Engine (PNX-FX-ARCH-001).
 * Supports Western Short, Indian Lakhs/Crores, European Long, Cheque Fractions & Anti-Fraud Star Padding.
 */
import { Money } from './Money';

export type NumberingScale = 'WESTERN_SHORT' | 'INDIAN_LAKHS' | 'EUROPEAN_LONG' | 'MYRIAD';
export type CasingStyle = 'TITLE_CASE' | 'UPPERCASE' | 'LOWERCASE' | 'SENTENCE_CASE';
export type SubunitFormat = 'WORDS' | 'FRACTION_100' | 'FRACTION_1000' | 'NONE';

export interface AmountInWordsOptions {
  readonly scale?: NumberingScale;
  readonly casing?: CasingStyle;
  readonly subunitFormat?: SubunitFormat;
  readonly starPadding?: boolean;
  readonly includeOnlySuffix?: boolean;
  readonly mainUnitName?: string;
  readonly subunitName?: string;
}

const ONES = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine'];
const TEENS = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
const TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];

const CURRENCY_NAMES: Record<string, { main: string; sub: string; decimals: number }> = {
  INR: { main: 'Rupees', sub: 'Paise', decimals: 2 },
  USD: { main: 'Dollars', sub: 'Cents', decimals: 2 },
  EUR: { main: 'Euros', sub: 'Cents', decimals: 2 },
  GBP: { main: 'Pounds', sub: 'Pence', decimals: 2 },
  AED: { main: 'Dirhams', sub: 'Fils', decimals: 2 },
  SAR: { main: 'Riyals', sub: 'Halalas', decimals: 2 },
  KWD: { main: 'Dinars', sub: 'Fils', decimals: 3 },
  JPY: { main: 'Yen', sub: '', decimals: 0 },
};

export class AmountInWordsEngine {
  public static toWords(money: Money, options: AmountInWordsOptions = {}): string {
    const rawUnits = money.getRawUnits();
    const absUnits = rawUnits < 0n ? -rawUnits : rawUnits;
    const intUnits = absUnits / 10000n;
    const fracUnits = absUnits % 10000n;

    const currMeta = CURRENCY_NAMES[money.currency] ?? { main: money.currency, sub: 'Cents', decimals: 2 };
    const mainUnit = options.mainUnitName ?? currMeta.main;
    const subUnit = options.subunitName ?? currMeta.sub;
    const scale = options.scale ?? (money.currency === 'INR' ? 'INDIAN_LAKHS' : 'WESTERN_SHORT');

    const intWords = intUnits === 0n ? 'Zero' : this.convertInteger(intUnits, scale);
    const fracWords = this.convertFraction(fracUnits, currMeta.decimals, subUnit, options.subunitFormat ?? 'WORDS');

    let body = `${intWords} ${mainUnit}`;
    if (fracWords.length > 0) {
      body += ` and ${fracWords}`;
    }

    if (options.includeOnlySuffix !== false) {
      body += ' Only';
    }

    const styled = this.applyCasing(body, options.casing ?? 'TITLE_CASE');
    return options.starPadding ? `*** ${styled} ***` : styled;
  }

  private static convertInteger(num: bigint, scale: NumberingScale): string {
    if (scale === 'INDIAN_LAKHS') {
      return this.convertIndianScale(num);
    }
    return this.convertWesternScale(num);
  }

  private static convertWesternScale(num: bigint): string {
    const scales = ['', 'Thousand', 'Million', 'Billion', 'Trillion'];
    const chunks: string[] = [];
    let rem = num;
    let scaleIdx = 0;

    while (rem > 0n && scaleIdx < scales.length) {
      const chunk = Number(rem % 1000n);
      if (chunk > 0) {
        const chunkWords = this.convertThreeDigits(chunk);
        const scaleWord = scales[scaleIdx];
        chunks.unshift(scaleWord ? `${chunkWords} ${scaleWord}` : chunkWords);
      }
      rem = rem / 1000n;
      scaleIdx++;
    }
    return chunks.join(' ').trim();
  }

  private static convertIndianScale(num: bigint): string {
    if (num < 1000n) return this.convertThreeDigits(Number(num));
    const parts: string[] = [];
    let rem = num;

    const lastThree = Number(rem % 1000n);
    if (lastThree > 0) parts.unshift(this.convertThreeDigits(lastThree));
    rem = rem / 1000n;

    const denominations = ['Thousand', 'Lakh', 'Crore', 'Arab'];
    let idx = 0;
    while (rem > 0n && idx < denominations.length) {
      const chunk = Number(rem % 100n);
      if (chunk > 0) {
        parts.unshift(`${this.convertTwoDigits(chunk)} ${denominations[idx]}`);
      }
      rem = rem / 100n;
      idx++;
    }
    return parts.join(' ').trim();
  }

  private static convertThreeDigits(n: number): string {
    const hundreds = Math.floor(n / 100);
    const rem = n % 100;
    const parts: string[] = [];
    if (hundreds > 0) parts.push(`${ONES[hundreds]} Hundred`);
    if (rem > 0) parts.push(this.convertTwoDigits(rem));
    return parts.join(' ');
  }

  private static convertTwoDigits(n: number): string {
    if (n < 10) return ONES[n];
    if (n < 20) return TEENS[n - 10];
    const tens = Math.floor(n / 10);
    const rem = n % 10;
    return rem > 0 ? `${TENS[tens]} ${ONES[rem]}` : TENS[tens];
  }

  private static convertFraction(fracRaw: bigint, decimals: number, subUnitName: string, fmt: SubunitFormat): string {
    if (decimals === 0 || fmt === 'NONE' || fracRaw === 0n) return '';
    const fracStr = fracRaw.toString().padStart(4, '0').slice(0, decimals);
    const fracVal = parseInt(fracStr, 10);
    if (fracVal === 0) return '';

    if (fmt === 'FRACTION_100') return `${fracVal}/100`;
    if (fmt === 'FRACTION_1000') return `${fracVal}/1000`;
    const words = this.convertTwoDigits(fracVal);
    return subUnitName ? `${words} ${subUnitName}` : words;
  }

  private static applyCasing(text: string, casing: CasingStyle): string {
    if (casing === 'UPPERCASE') return text.toUpperCase();
    if (casing === 'LOWERCASE') return text.toLowerCase();
    if (casing === 'SENTENCE_CASE') {
      return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
    }
    return text;
  }
}
