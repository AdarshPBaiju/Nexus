import React from 'react';

export interface NexusDividerProps {
  readonly orientation?: 'horizontal' | 'vertical';
  readonly className?: string;
}

export function NexusDivider({
  orientation = 'horizontal',
  className = '',
}: NexusDividerProps): React.JSX.Element {
  const dividerStyle: React.CSSProperties =
    orientation === 'horizontal'
      ? {
          height: '1px',
          width: '100%',
          backgroundColor: 'var(--nx-border-divider)',
          border: 'none',
          margin: 'var(--nx-space-2) 0',
        }
      : {
          width: '1px',
          height: '100%',
          backgroundColor: 'var(--nx-border-divider)',
          border: 'none',
          margin: '0 var(--nx-space-2)',
        };

  return <div style={dividerStyle} role="separator" className={className} />;
}
