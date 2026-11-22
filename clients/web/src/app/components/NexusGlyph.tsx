import React from 'react';
import { GLYPH_SHAPES, type GlyphName } from './glyphShapes';

export type { GlyphName };

export interface NexusGlyphProps {
  readonly name: GlyphName;
  readonly size?: number;
  readonly color?: string;
  readonly style?: React.CSSProperties;
}

export function NexusGlyph({
  name,
  size = 18,
  color = 'currentColor',
  style = {},
}: NexusGlyphProps): React.JSX.Element {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      style={{ display: 'inline-block', flexShrink: 0, verticalAlign: 'middle', ...style }}
    >
      {GLYPH_SHAPES[name] ?? null}
    </svg>
  );
}
