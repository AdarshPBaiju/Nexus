'use client';

import React from 'react';
import {
  NexusDateInput,
  NexusDateRangeInput,
  NexusTimeInput,
} from '@nexus/ui';
import type { DateRange } from '@nexus/ui';
import { StudioSection } from './StudioSection';

export interface StudioDateTimeSectionProps {
  readonly openedOn: string;
  readonly onChangeOpenedOn: (v: string) => void;
  readonly shiftStart: string;
  readonly onChangeShiftStart: (v: string) => void;
  readonly period: DateRange;
  readonly onChangePeriod: (v: DateRange) => void;
  readonly isDisabled: boolean;
  readonly errorKey?: string;
}

export function StudioDateTimeSection({
  openedOn,
  onChangeOpenedOn,
  shiftStart,
  onChangeShiftStart,
  period,
  onChangePeriod,
  isDisabled,
  errorKey,
}: StudioDateTimeSectionProps): React.JSX.Element {
  return (
    <StudioSection
      index="03"
      title="Dates, Times & Ranges"
      description="Strict ISO-formatted date, time, and range inputs with native picker integration."
    >
      <div className="nx-studio-fields">
        <NexusDateInput
          labelKey="Batch Opening Date"
          value={openedOn}
          onChange={onChangeOpenedOn}
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
        <NexusTimeInput
          labelKey="Shift Roster Start"
          value={shiftStart}
          onChange={onChangeShiftStart}
          isDisabled={isDisabled}
          errorKey={errorKey}
        />
      </div>
      <NexusDateRangeInput
        labelKey="Fiscal Reconciliation Window"
        value={period}
        onChange={onChangePeriod}
        isDisabled={isDisabled}
        errorKey={errorKey}
      />
    </StudioSection>
  );
}
