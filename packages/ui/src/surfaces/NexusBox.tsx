import React from 'react';

export interface NexusBoxProps {
  readonly padding?: string;
  readonly margin?: string;
  readonly className?: string;
  readonly style?: React.CSSProperties;
  readonly children?: React.ReactNode;
}

export function NexusBox({
  padding,
  margin,
  className = '',
  style = {},
  children,
}: NexusBoxProps): React.JSX.Element {
  const boxStyle: React.CSSProperties = {
    padding,
    margin,
    ...style,
  };

  return (
    <div style={boxStyle} className={className}>
      {children}
    </div>
  );
}
