'use client';

import React from 'react';
import {
  NexusCheckbox,
  NexusCheckboxGroup,
  NexusMultiSelect,
  NexusRadioGroup,
  NexusSelect,
  NexusSwitch,
} from '@nexus/ui';
import { StudioSection } from './StudioSection';

export interface StudioChoiceSectionProps {
  readonly station: string;
  readonly onChangeStation: (v: string) => void;
  readonly channels: readonly string[];
  readonly onChangeChannels: (v: readonly string[]) => void;
  readonly plan: string;
  readonly onChangePlan: (v: string) => void;
  readonly permissions: readonly string[];
  readonly onChangePermissions: (v: readonly string[]) => void;
  readonly isTaxable: boolean;
  readonly onChangeIsTaxable: (v: boolean) => void;
  readonly allowBackorder: boolean;
  readonly onChangeAllowBackorder: (v: boolean) => void;
  readonly stationOptions: readonly { value: string; label: string }[];
  readonly channelOptions: readonly { value: string; label: string }[];
  readonly planOptions: readonly { value: string; label: string }[];
  readonly permissionOptions: readonly { value: string; label: string }[];
  readonly isDisabled: boolean;
  readonly errorKey?: string;
}

export function StudioChoiceSection({
  station,
  onChangeStation,
  channels,
  onChangeChannels,
  plan,
  onChangePlan,
  permissions,
  onChangePermissions,
  isTaxable,
  onChangeIsTaxable,
  allowBackorder,
  onChangeAllowBackorder,
  stationOptions,
  channelOptions,
  planOptions,
  permissionOptions,
  isDisabled,
  errorKey,
}: StudioChoiceSectionProps): React.JSX.Element {
  return (
    <StudioSection
      index="02"
      title="Selections, Radios & Switches"
      description="Single and multi-choice selectors with accessible focus indicators."
    >
      <div className="nx-studio-fields">
        <NexusSelect
          labelKey="Preparation Station"
          value={station}
          onChange={onChangeStation}
          options={stationOptions}
          isRequired
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
        <NexusMultiSelect
          labelKey="Enabled Order Channels"
          value={channels}
          onChange={onChangeChannels}
          options={channelOptions}
          placeholderKey="Choose channels..."
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
      </div>
      <div className="nx-studio-fields">
        <NexusRadioGroup
          name="subscriptionPlan"
          labelKey="SaaS Subscription Tier"
          value={plan}
          onChange={onChangePlan}
          options={planOptions}
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
        <NexusCheckboxGroup
          labelKey="Staff Role Capabilities"
          value={permissions}
          onChange={onChangePermissions}
          options={permissionOptions}
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
      </div>
      <div className="nx-studio-fields">
        <NexusSwitch
          labelKey="Statutory Tax Application"
          descriptionKey="Apply standard café sales tax at POS"
          value={isTaxable}
          onChange={onChangeIsTaxable}
          isDisabled={isDisabled}
        />
        <NexusCheckbox
          labelKey="Allow POS sale when stock is zero"
          descriptionKey="Enables negative inventory override"
          value={allowBackorder}
          onChange={onChangeAllowBackorder}
          isDisabled={isDisabled}
        />
      </div>
    </StudioSection>
  );
}
