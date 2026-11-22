'use client';

import React from 'react';
import { NexusSearchInput, NexusTextarea, NexusTextInput } from '@nexus/ui';
import { StudioSection } from './StudioSection';

export interface StudioTextSectionProps {
  readonly itemName: string;
  readonly onChangeItemName: (v: string) => void;
  readonly searchQuery: string;
  readonly onChangeSearchQuery: (v: string) => void;
  readonly notes: string;
  readonly onChangeNotes: (v: string) => void;
  readonly isDisabled: boolean;
  readonly errorKey?: string;
}

export function StudioTextSection({
  itemName,
  onChangeItemName,
  searchQuery,
  onChangeSearchQuery,
  notes,
  onChangeNotes,
  isDisabled,
  errorKey,
}: StudioTextSectionProps): React.JSX.Element {
  return (
    <StudioSection
      index="01"
      title="Text, Search & Descriptions"
      description="Fundamental string and search controls with validation hints and clear buttons."
    >
      <div className="nx-studio-fields">
        <NexusTextInput
          labelKey="Menu Item Name"
          value={itemName}
          onChange={onChangeItemName}
          placeholderKey="e.g. Signature Flat White"
          isRequired
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
        <NexusSearchInput
          value={searchQuery}
          onChange={onChangeSearchQuery}
          placeholderKey="Scan barcode or type SKU..."
        />
      </div>
      <NexusTextarea
        labelKey="Preparation Notes"
        value={notes}
        onChange={onChangeNotes}
        placeholderKey="Add special instructions for kitchen/barista..."
        maxLength={240}
        isDisabled={isDisabled}
        errorKey={errorKey}
      />
    </StudioSection>
  );
}
