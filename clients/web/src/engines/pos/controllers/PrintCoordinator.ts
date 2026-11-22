/**
 * PrintCoordinator.ts - Hardware printer routing and dispatch coordinator for POS.
 */

export interface PrintDispatchResult {
  readonly receiptPrinted: boolean;
  readonly drawerKickFired: boolean;
  readonly kotStationsDispatched: readonly string[];
  readonly timestamp: string;
}

export interface PrintLineItem {
  readonly name: string;
  readonly quantity: number;
  readonly station: 'BARISTA' | 'HOT_KITCHEN' | 'BAKERY' | 'DESSERT' | 'COLD_BAR';
}

export class PrintCoordinator {
  public static shouldKickDrawer(tenders: readonly { readonly tenderType: string }[]): boolean {
    return tenders.some((t) => t.tenderType === 'CASH');
  }

  public static routeKitchenTickets(
    items: readonly PrintLineItem[],
  ): Record<string, PrintLineItem[]> {
    const routing: Record<string, PrintLineItem[]> = {};
    for (const item of items) {
      const station = item.station;
      if (!routing[station]) {
        routing[station] = [];
      }
      routing[station].push(item);
    }
    return routing;
  }

  public static async dispatchPrint(
    orderNumber: string,
    items: readonly PrintLineItem[],
    tenders: readonly { readonly tenderType: string }[],
  ): Promise<PrintDispatchResult> {
    const shouldKick = this.shouldKickDrawer(tenders);
    const stationRoutes = this.routeKitchenTickets(items);
    const stations = Object.keys(stationRoutes);

    return {
      receiptPrinted: true,
      drawerKickFired: shouldKick,
      kotStationsDispatched: stations,
      timestamp: new Date().toISOString(),
    };
  }
}
