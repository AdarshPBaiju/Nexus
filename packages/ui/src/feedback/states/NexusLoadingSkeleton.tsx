import React from 'react';

export interface NexusLoadingSkeletonProps {
  readonly width?: string;
  readonly height?: string;
  readonly borderRadius?: string;
  readonly className?: string;
}

export function NexusLoadingSkeleton({
  width = '100%',
  height = '20px',
  borderRadius = '4px',
  className = '',
}: NexusLoadingSkeletonProps): React.JSX.Element {
  const skeletonStyle: React.CSSProperties = {
    width,
    height,
    borderRadius,
    backgroundColor: 'var(--nx-surface-subtle)',
    animation: 'pulse 1.5s ease-in-out infinite',
  };

  return <div style={skeletonStyle} className={className} aria-busy="true" />;
}
