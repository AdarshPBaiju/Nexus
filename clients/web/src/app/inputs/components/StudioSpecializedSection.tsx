'use client';

import React from 'react';
import {
  NexusColorPicker,
  NexusFileInput,
  NexusLocalizedTextInput,
  NexusMoneyInput,
  NexusNumberInput,
  NexusSelect,
  NexusPinInput,
  NexusSlider,
} from '@nexus/ui';
import type { LocalizedStringMap } from '@nexus/ui';
import type { Money } from '@nexus/contracts';
import { StudioSection } from './StudioSection';

export interface StudioSpecializedSectionProps {
  readonly unitPrice: Money;
  readonly onChangeUnitPrice: (v: Money) => void;
  readonly safetyStock: number;
  readonly onChangeSafetyStock: (v: number) => void;
  readonly wasteAllowance: number;
  readonly onChangeWasteAllowance: (v: number) => void;
  readonly managerPin: string;
  readonly onChangeManagerPin: (v: string) => void;
  readonly brandColor: string;
  readonly onChangeBrandColor: (v: string) => void;
  readonly attachment: File | null;
  readonly onChangeAttachment: (v: File | null) => void;
  readonly locale: string;
  readonly onChangeLocale: (v: string) => void;
  readonly labels: LocalizedStringMap;
  readonly onChangeLabels: (v: LocalizedStringMap) => void;
  readonly isDisabled: boolean;
  readonly errorKey?: string;
}

export function StudioSpecializedSection({
  unitPrice,
  onChangeUnitPrice,
  safetyStock,
  onChangeSafetyStock,
  wasteAllowance,
  onChangeWasteAllowance,
  managerPin,
  onChangeManagerPin,
  brandColor,
  onChangeBrandColor,
  attachment,
  onChangeAttachment,
  locale,
  onChangeLocale,
  labels,
  onChangeLabels,
  isDisabled,
  errorKey,
}: StudioSpecializedSectionProps): React.JSX.Element {
  return (
    <>
      <StudioSection
        index="04"
        title="Money, Numbers & PIN Security"
        description="Exact string-decimal currency math, numeric step steppers, and secret PIN pads."
      >
        <div className="nx-studio-fields">
          <NexusMoneyInput
            labelKey="Base Retail Price"
            value={unitPrice}
            onChange={onChangeUnitPrice}
            isRequired
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <NexusNumberInput
            labelKey="Threshold Safety Stock"
            value={safetyStock}
            onChange={onChangeSafetyStock}
            min={0}
            max={200}
            step={1}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
        </div>
        <div className="nx-studio-fields">
          <NexusPinInput
            labelKey="Manager Override PIN"
            value={managerPin}
            onChange={onChangeManagerPin}
            length={4}
            isMasked
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <NexusSlider
            labelKey="Recipe Waste Allowance"
            value={wasteAllowance}
            onChange={onChangeWasteAllowance}
            min={0}
            max={50}
            step={5}
            isDisabled={isDisabled}
          />
        </div>
      </StudioSection>

      <StudioSection
        index="05"
        title="Localization, Media & Theming"
        description="Multilingual dictionary editors, color tokens, and asset dropzones."
      >
        <NexusSelect
          labelKey="Active Locale"
          value={locale}
          onChange={onChangeLocale}
          options={[
            { value: 'en', label: 'English (US)' },
            { value: 'ar', label: 'العربية (RTL)' },
            { value: 'fr', label: 'Français' },
          ]}
          isDisabled={isDisabled}
        />
        <NexusLocalizedTextInput
          labelKey="Multilingual Display Name"
          value={labels}
          onChange={onChangeLabels}
          activeLocale={locale}
          availableLocales={['en', 'ar', 'fr']}
          isRequired
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
        <div className="nx-studio-fields">
          <NexusColorPicker
            labelKey="Station Accent Hue"
            value={brandColor}
            onChange={onChangeBrandColor}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <NexusFileInput
            labelKey="Recipe Spec Sheet (PDF/PNG)"
            value={attachment}
            onChange={onChangeAttachment}
            accept=".pdf,.png,.jpg"
            isDisabled={isDisabled}
          />
        </div>
      </StudioSection>
    </>
  );
}
