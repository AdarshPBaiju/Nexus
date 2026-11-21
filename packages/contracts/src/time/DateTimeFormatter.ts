/**
 * DateTimeFormatter - Timezone and business operational date conversion utilities.
 */
export class DateTimeFormatter {
  public static toZonedString(utcIsoString: string, timeZone: string): string {
    const date = new Date(utcIsoString);
    return new Intl.DateTimeFormat('en-CA', {
      timeZone,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
    }).format(date);
  }

  public static getOperationalBusinessDate(
    utcTimestamp: string | Date,
    timeZone: string,
    cutoffHour: number = 4
  ): string {
    const date = typeof utcTimestamp === 'string' ? new Date(utcTimestamp) : utcTimestamp;
    // Format to local parts
    const parts = new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      hour12: false,
    }).formatToParts(date);

    let year = 0;
    let month = 0;
    let day = 0;
    let hour = 0;

    for (const p of parts) {
      if (p.type === 'year') year = parseInt(p.value, 10);
      if (p.type === 'month') month = parseInt(p.value, 10);
      if (p.type === 'day') day = parseInt(p.value, 10);
      if (p.type === 'hour') hour = parseInt(p.value, 10);
    }

    // If local hour is before cutoffHour, business date is previous calendar day
    const localCalDate = new Date(Date.UTC(year, month - 1, day));
    if (hour < cutoffHour) {
      localCalDate.setUTCDate(localCalDate.getUTCDate() - 1);
    }

    const y = localCalDate.getUTCFullYear();
    const m = String(localCalDate.getUTCMonth() + 1).padStart(2, '0');
    const d = String(localCalDate.getUTCDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
}
