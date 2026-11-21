import React from 'react';

export type IconSize = 'sm' | 'md' | 'lg' | 'xl';

export type StandardIconName =
  | 'search'
  | 'filter'
  | 'plus'
  | 'check'
  | 'close'
  | 'chevron-down'
  | 'chevron-right'
  | 'chevron-left'
  | 'chevron-up'
  | 'trash'
  | 'edit'
  | 'more-vertical'
  | 'user'
  | 'building'
  | 'settings'
  | 'alert-triangle'
  | 'info'
  | 'lock'
  | 'download'
  | 'upload';

export interface NexusIconProps {
  readonly name: StandardIconName;
  readonly size?: IconSize;
  readonly className?: string;
  readonly style?: React.CSSProperties;
}

const SIZE_MAP: Record<IconSize, number> = {
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

export function NexusIcon({
  name,
  size = 'md',
  className = '',
  style = {},
}: NexusIconProps): React.JSX.Element {
  const pixelSize = SIZE_MAP[size];

  return (
    <svg
      width={pixelSize}
      height={pixelSize}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      style={{ display: 'inline-block', verticalAlign: 'middle', ...style }}
      aria-hidden="true"
    >
      {name === 'check' && <polyline points="20 6 9 17 4 12" />}
      {name === 'close' && (
        <>
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </>
      )}
      {name === 'plus' && (
        <>
          <line x1="12" y1="5" x2="12" y2="19" />
          <line x1="5" y1="12" x2="19" y2="12" />
        </>
      )}
      {name === 'search' && (
        <>
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </>
      )}
      {name === 'chevron-down' && <polyline points="6 9 12 15 18 9" />}
      {name === 'chevron-right' && <polyline points="9 18 15 12 9 6" />}
      {name === 'chevron-left' && <polyline points="15 18 9 12 15 6" />}
      {name === 'chevron-up' && <polyline points="18 15 12 9 6 15" />}
      {name === 'filter' && <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />}
      {name === 'trash' && (
        <>
          <polyline points="3 6 5 6 21 6" />
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        </>
      )}
      {name === 'edit' && (
        <>
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
        </>
      )}
      {name === 'user' && (
        <>
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </>
      )}
      {name === 'settings' && (
        <>
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </>
      )}
      {!['check', 'close', 'plus', 'search', 'chevron-down', 'chevron-right', 'chevron-left', 'chevron-up', 'filter', 'trash', 'edit', 'user', 'settings'].includes(name) && (
        <circle cx="12" cy="12" r="10" />
      )}
    </svg>
  );
}
