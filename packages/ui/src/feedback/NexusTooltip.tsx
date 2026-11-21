import React from 'react';
import { SurfaceProvider } from '../theme/SurfaceContext';
import { NexusText } from '../typography/NexusText';

export interface NexusTooltipProps {
  readonly content: string;
  readonly children: React.ReactNode;
}

export function NexusTooltip({ content, children }: NexusTooltipProps): React.JSX.Element {
  const tooltipStyle: React.CSSProperties = {
    position: 'relative',
    display: 'inline-flex',
  };

  const bubbleStyle: React.CSSProperties = {
    backgroundColor: 'var(--nx-surface-tooltip)',
    padding: 'var(--nx-space-1) var(--nx-space-2)',
    borderRadius: '4px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
  };

  return (
    <span style={tooltipStyle} title={content}>
      {children}
      <SurfaceProvider role="tooltip">
        <span style={{ display: 'none' }} className="nexus-tooltip-bubble">
          <span style={bubbleStyle}>
            <NexusText variant="caption">{content}</NexusText>
          </span>
        </span>
      </SurfaceProvider>
    </span>
  );
}
