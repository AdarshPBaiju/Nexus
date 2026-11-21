import { Money } from './Money';

export interface MoneyFormatOptions {
  readonly locale?: string;
  readonly displayCurrency?: boolean;
  readonly minorUnitDecimals?: number;
}

export class MoneyFormatter {
  public static format(money: Money, options: MoneyFormatOptions = {}): string {
    const locale = options.locale || 'en-US';
    const displayCurrency = options.displayCurrency !== false;
    const decimals = options.minorUnitDecimals !== undefined ? options.minorUnitDecimals : 2;

    const num = Number(money.amount);
    const formattedNum = new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);

    if (displayCurrency) {
      return `${money.currency} ${formattedNum}`;
    }
    return formattedNum;
  }
}
