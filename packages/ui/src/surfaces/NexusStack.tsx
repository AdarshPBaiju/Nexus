import React from 'react';

export interface NexusStackProps {
  readonly direction?: 'row' | 'column';
  readonly gap?: string;
  readonly align?: 'start' | 'center' | 'end' | 'stretch';
  readonly justify?: 'start' | 'center' | 'end' | 'space-between';
  readonly className?: string;
  readonly children: React.ReactNode;
}

export function NexusStack({
  direction = 'column',
  gap = 'var(--nx-space-4)',
  align = 'stretch',
  justify = 'start',
  className = '',
  children,
}: NexusStackProps): React.JSX.Element {
  const stackStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: direction,
    gap,
    alignItems: align,
    justifyContent: justify,
  };

  return (
    <div style={stackStyle} className={className}>
      {children}
    </div>
  );
}
