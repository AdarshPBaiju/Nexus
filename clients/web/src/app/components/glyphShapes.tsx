import React from 'react';

export type GlyphName =
  | 'apps'
  | 'storefront'
  | 'menu'
  | 'menu_open'
  | 'search'
  | 'search_off'
  | 'lock'
  | 'light_mode'
  | 'dark_mode'
  | 'schedule'
  | 'dashboard'
  | 'tune'
  | 'point_of_sale'
  | 'skillet'
  | 'inventory_2'
  | 'payments'
  | 'credit_card'
  | 'badge'
  | 'receipt_long'
  | 'domain_add'
  | 'shopping_bag'
  | 'close'
  | 'check_circle'
  | 'backspace'
  | 'cloud_upload'
  | 'verified'
  | 'local_cafe'
  | 'print'
  | 'terminal'
  | 'extension'
  | 'hub'
  | 'sync'
  | 'security'
  | 'swap_horiz'
  | 'expand_more'
  | 'expand_less'
  | 'check';

export const GLYPH_SHAPES: Record<GlyphName, React.JSX.Element> = {
  apps: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </>
  ),
  storefront: (
    <>
      <path d="M4 10v10h16V10" />
      <path d="M3 10l2-6h14l2 6" />
      <path d="M3 10a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0" />
      <path d="M9 20v-5h6v5" />
    </>
  ),
  menu: <path d="M4 7h16M4 12h16M4 17h16" />,
  menu_open: (
    <>
      <path d="M4 7h10M4 12h10M4 17h10" />
      <path d="M18 8l-3 4 3 4" />
    </>
  ),
  search: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </>
  ),
  search_off: (
    <>
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5M4 4l16 16" />
    </>
  ),
  lock: (
    <>
      <rect x="5" y="10" width="14" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </>
  ),
  light_mode: (
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19" />
    </>
  ),
  dark_mode: <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z" />,
  schedule: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  dashboard: (
    <>
      <rect x="3" y="3" width="8" height="10" rx="1.5" />
      <rect x="13" y="3" width="8" height="6" rx="1.5" />
      <rect x="13" y="11" width="8" height="10" rx="1.5" />
      <rect x="3" y="15" width="8" height="6" rx="1.5" />
    </>
  ),
  tune: (
    <>
      <path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0" />
      <circle cx="16" cy="6" r="2" />
      <circle cx="10" cy="12" r="2" />
      <circle cx="18" cy="18" r="2" />
    </>
  ),
  point_of_sale: (
    <>
      <path d="M6 9h12l-1 11H7L6 9z" />
      <path d="M9 9V5h6v4" />
      <path d="M9 14h6" />
    </>
  ),
  skillet: (
    <>
      <circle cx="10" cy="12" r="6" />
      <path d="M16 12h5" />
      <path d="M8 9h4" />
    </>
  ),
  inventory_2: (
    <>
      <path d="M3 7l9-4 9 4-9 4-9-4z" />
      <path d="M3 7v10l9 4 9-4V7" />
      <path d="M12 11v10" />
    </>
  ),
  payments: (
    <>
      <rect x="2" y="6" width="20" height="12" rx="2" />
      <circle cx="12" cy="12" r="2.5" />
      <path d="M6 10h.01M18 14h.01" />
    </>
  ),
  credit_card: (
    <>
      <rect x="2" y="5" width="20" height="14" rx="2" />
      <path d="M2 10h20M6 15h4" />
    </>
  ),
  badge: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="11" r="2.5" />
      <path d="M14 9h4M14 13h4M6 17c1-2 2.5-3 4-3s3 1 4 3" />
    </>
  ),
  receipt_long: (
    <>
      <path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2V3z" />
      <path d="M9 8h6M9 12h6M9 16h4" />
    </>
  ),
  domain_add: (
    <>
      <path d="M4 21V5a2 2 0 0 1 2-2h7a2 2 0 0 1 2 2v16" />
      <path d="M2 21h13M8 7h3M8 11h3M8 15h3" />
      <path d="M18 12v8M14 16h8" />
    </>
  ),
  shopping_bag: (
    <>
      <path d="M5 8h14l-1 13H6L5 8z" />
      <path d="M9 8V6a3 3 0 0 1 6 0v2" />
    </>
  ),
  close: <path d="M6 6l12 12M18 6L6 18" />,
  check_circle: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12l3 3 5-6" />
    </>
  ),
  backspace: (
    <>
      <path d="M9 5h11v14H9L3 12l6-7z" />
      <path d="M12 9l4 6M16 9l-4 6" />
    </>
  ),
  cloud_upload: (
    <>
      <path d="M7 18a4 4 0 0 1-.5-8A5.5 5.5 0 0 1 17 9a3.5 3.5 0 0 1 .5 7" />
      <path d="M12 12v8M9 15l3-3 3 3" />
    </>
  ),
  verified: (
    <>
      <path d="M12 3l2.4 1.7 3-.2 1 2.8 2.4 1.8-1 2.9 1 2.9-2.4 1.8-1 2.8-3-.2L12 21l-2.4-1.7-3 .2-1-2.8L3.2 15l1-2.9-1-2.9 2.4-1.8 1-2.8 3 .2L12 3z" />
      <path d="M8.5 12l2.5 2.5 4.5-5" />
    </>
  ),
  local_cafe: (
    <>
      <path d="M4 8h12v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8z" />
      <path d="M16 9h2a2.5 2.5 0 0 1 0 5h-2" />
      <path d="M4 21h13M7 4c0-1 1-1 1-2M11 4c0-1 1-1 1-2" />
    </>
  ),
  print: (
    <>
      <path d="M6 8V3h12v5" />
      <rect x="3" y="8" width="18" height="8" rx="2" />
      <path d="M6 14h12v7H6z" />
    </>
  ),
  terminal: (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="M7 9l3 3-3 3M13 15h4" />
    </>
  ),
  extension: (
    <path d="M19 11h-2a2 2 0 0 1-2-2V7a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v2a2 2 0 0 1-2 2H3a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h2a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2a2 2 0 0 1 2-2h2a2 2 0 0 0 2-2v-4a2 2 0 0 0-2-2z" />
  ),
  hub: (
    <>
      <circle cx="12" cy="12" r="3" />
      <circle cx="5" cy="6" r="2" />
      <circle cx="19" cy="6" r="2" />
      <circle cx="5" cy="18" r="2" />
      <circle cx="19" cy="18" r="2" />
      <path d="M7 7l3 3M14 14l3 3M17 7l-3 3M10 14l-3 3" />
    </>
  ),
  sync: <path d="M21.5 2v6h-6M21.34 15.57a9 9 0 1 1-.57-8.38l.67-.79" />,
  security: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />,
  swap_horiz: <path d="M8 7l-4 4 4 4M4 11h16M16 17l4-4-4-4" />,
  expand_more: <path d="m6 9 6 6 6-6" />,
  expand_less: <path d="m18 15-6-6-6 6" />,
  check: <path d="M20 6 9 17l-5-5" />,
};
