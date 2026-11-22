/**
 * packages/contracts/src/money/MoneyFormatter.ts
 *
 * 100% Runtime-Configurable Dynamic Currency Formatter Engine (PNX-FX-ARCH-001).
 * Operates purely on string/BigInt primitives with ZERO floating-point loss.
 */
import { Money } from './Money';

export type SymbolPosition = 'PREFIX_BEFORE_SIGN' | 'PREFIX_AFTER_SIGN' | 'SUFFIX';
export type NegativeFormat = 'MINUS_PREFIX' | 'MINUS_SUFFIX' | 'ACCOUNTING_PARENS' | 'DR_CR_SUFFIX';
export type ZeroFormat = 'STANDARD' | 'DASH' | 'BLANK' | 'FREE_LABEL';
export type NumeralScript = 'LATIN' | 'ARABIC_INDIC' | 'EXTENDED_ARABIC_PERSIAN' | 'DEVANAGARI';
export type SymbolMode = 'UNICODE_SYMBOL' | 'ISO_CODE' | 'CUSTOM_TEXT' | 'NONE';
export type SymbolSpacing = 'NONE' | 'SPACE' | 'NBSP' | 'THIN_SPACE';
export type PositiveSignDisplay = 'NEVER' | 'EXPLICIT_PLUS' | 'EXCEPT_ZERO';

export interface MoneyFormatProfile {
  readonly currencyCode?: string;
  readonly displayDecimals?: number;
  readonly accountingDecimals?: number;
  readonly trimTrailingZeros?: boolean;
  readonly decimalSplitter?: string;
  readonly thousandsSplitter?: string;
  readonly groupingPattern?: readonly number[];
  readonly symbolMode?: SymbolMode;
  readonly customSymbolText?: string;
  readonly symbolPosition?: SymbolPosition;
  readonly symbolSpacing?: SymbolSpacing;
  readonly negativeFormat?: NegativeFormat;
  readonly zeroFormat?: ZeroFormat;
  readonly numeralScript?: NumeralScript;
  readonly bidiIsolation?: boolean;
  readonly positiveSignDisplay?: PositiveSignDisplay;
}

const DEFAULT_PROFILE: Required<Omit<MoneyFormatProfile, 'currencyCode' | 'customSymbolText'>> = {
  displayDecimals: 2,
  accountingDecimals: 2,
  trimTrailingZeros: false,
  decimalSplitter: '.',
  thousandsSplitter: ',',
  groupingPattern: [3],
  symbolMode: 'UNICODE_SYMBOL',
  symbolPosition: 'PREFIX_AFTER_SIGN',
  symbolSpacing: 'SPACE',
  negativeFormat: 'MINUS_PREFIX',
  zeroFormat: 'STANDARD',
  numeralScript: 'LATIN',
  bidiIsolation: false,
  positiveSignDisplay: 'NEVER',
};

const SYMBOL_MAP: Record<string, string> = {
  INR: '₹', USD: '$', EUR: '€', GBP: '£', AED: 'د.إ', SAR: 'ر.س',
  KWD: 'KD', JPY: '¥', CAD: 'CA$', AUD: 'A$', QAR: 'QR', OMR: 'OMR', BHD: 'BD',
};

const SCRIPT_DIGITS: Record<NumeralScript, string[]> = {
  LATIN: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
  ARABIC_INDIC: ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'],
  EXTENDED_ARABIC_PERSIAN: ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'],
  DEVANAGARI: ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'],
};

export class MoneyFormatter {
  public static format(money: Money, profileOverrides: MoneyFormatProfile = {}): string {
    const prof = { ...DEFAULT_PROFILE, ...profileOverrides };
    const rawUnits = money.getRawUnits();
    const isZero = rawUnits === 0n;
    const isNegative = rawUnits < 0n;

    if (isZero && prof.zeroFormat !== 'STANDARD') {
      return this.formatZeroState(prof);
    }

    const absUnits = isNegative ? -rawUnits : rawUnits;
    const decimals = prof.displayDecimals;
    const { intStr, fracStr } = this.splitUnitsToString(absUnits, decimals, prof.trimTrailingZeros);
    const groupedInt = this.applyGrouping(intStr, prof.thousandsSplitter, prof.groupingPattern);
    const numBody = fracStr.length > 0 ? `${groupedInt}${prof.decimalSplitter}${fracStr}` : groupedInt;
    const transliteratedBody = this.applyScript(numBody, prof.numeralScript);
    const symbolStr = this.resolveSymbol(money.currency, prof);

    const withSignAndSymbol = this.assembleComponents(transliteratedBody, symbolStr, isNegative, prof);
    return prof.bidiIsolation ? `<bdi dir="ltr">${withSignAndSymbol}</bdi>` : withSignAndSymbol;
  }

  private static formatZeroState(prof: Required<Omit<MoneyFormatProfile, 'currencyCode' | 'customSymbolText'>>): string {
    if (prof.zeroFormat === 'DASH') return '—';
    if (prof.zeroFormat === 'BLANK') return '';
    return 'FREE';
  }

  private static splitUnitsToString(units: bigint, decimals: number, trimZeros: boolean): { intStr: string; fracStr: string } {
    const scale = 4;
    const divisor = 10000n;
    const intPart = units / divisor;
    const fracRaw = units % divisor;
    let fracStr = fracRaw.toString().padStart(scale, '0');

    if (decimals <= scale) {
      fracStr = fracStr.slice(0, decimals);
    } else {
      fracStr = fracStr.padEnd(decimals, '0');
    }

    if (trimZeros && fracStr.length > 0) {
      fracStr = fracStr.replace(/0+$/, '');
    }
    return { intStr: intPart.toString(), fracStr };
  }

  private static applyGrouping(intStr: string, splitter: string, pattern: readonly number[]): string {
    if (!splitter || pattern.length === 0 || intStr.length <= pattern[0]) {
      return intStr;
    }
    const chunks: string[] = [];
    let remaining = intStr;
    let patternIdx = 0;

    while (remaining.length > 0) {
      const takeSize = pattern[Math.min(patternIdx, pattern.length - 1)];
      if (remaining.length <= takeSize) {
        chunks.unshift(remaining);
        break;
      }
      const splitAt = remaining.length - takeSize;
      chunks.unshift(remaining.slice(splitAt));
      remaining = remaining.slice(0, splitAt);
      patternIdx++;
    }
    return chunks.join(splitter);
  }

  private static applyScript(value: string, script: NumeralScript): string {
    if (script === 'LATIN') return value;
    const targetDigits = SCRIPT_DIGITS[script];
    let result = '';
    for (let i = 0; i < value.length; i++) {
      const ch = value[i];
      const digitVal = ch.charCodeAt(0) - 48;
      result += (digitVal >= 0 && digitVal <= 9) ? targetDigits[digitVal] : ch;
    }
    return result;
  }

  private static resolveSymbol(currency: string, prof: MoneyFormatProfile): string {
    const mode = prof.symbolMode ?? 'UNICODE_SYMBOL';
    if (mode === 'NONE') return '';
    if (mode === 'ISO_CODE') return currency;
    if (mode === 'CUSTOM_TEXT' && prof.customSymbolText) return prof.customSymbolText;
    return SYMBOL_MAP[currency] ?? currency;
  }

  private static assembleComponents(
    body: string,
    symbol: string,
    isNegative: boolean,
    prof: Required<Omit<MoneyFormatProfile, 'currencyCode' | 'customSymbolText'>>
  ): string {
    const spacing = prof.symbolSpacing === 'NONE' ? '' : (prof.symbolSpacing === 'NBSP' ? '\u00A0' : ' ');
    const hasSymbol = symbol.length > 0;
    const plusPrefix = (!isNegative && prof.positiveSignDisplay === 'EXPLICIT_PLUS') ? '+' : '';

    if (!isNegative) {
      if (!hasSymbol) return `${plusPrefix}${body}`;
      return prof.symbolPosition === 'SUFFIX' ? `${plusPrefix}${body}${spacing}${symbol}` : `${symbol}${spacing}${plusPrefix}${body}`;
    }

    return this.applyNegativeForm(body, symbol, spacing, hasSymbol, prof.negativeFormat);
  }

  private static applyNegativeForm(body: string, sym: string, sp: string, hasSym: boolean, fmt: NegativeFormat): string {
    if (fmt === 'ACCOUNTING_PARENS') {
      return hasSym ? `(${sym}${sp}${body})` : `(${body})`;
    }
    if (fmt === 'MINUS_SUFFIX') {
      return hasSym ? `${sym}${sp}${body}-` : `${body}-`;
    }
    if (fmt === 'DR_CR_SUFFIX') {
      return hasSym ? `${sym}${sp}${body} DR` : `${body} DR`;
    }
    return hasSym ? `-${sym}${sp}${body}` : `-${body}`;
  }
}
