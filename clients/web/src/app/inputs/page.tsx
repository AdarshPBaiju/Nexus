'use client';

import React, { useMemo, useState } from 'react';
import { NexusBadge, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import type { DateRange, LocalizedStringMap } from '@nexus/ui';
import { Money } from '@nexus/contracts';
import { StudioInspector } from './components/StudioInspector';
import { StudioTextSection } from './components/StudioTextSection';
import { StudioChoiceSection } from './components/StudioChoiceSection';
import { StudioDateTimeSection } from './components/StudioDateTimeSection';
import { StudioSpecializedSection } from './components/StudioSpecializedSection';

type PreviewState = 'default' | 'error' | 'disabled';

const STATION_OPTIONS = [
  { value: 'BARISTA', label: 'Barista bar' },
  { value: 'COLD_BAR', label: 'Cold bar' },
  { value: 'HOT_KITCHEN', label: 'Hot kitchen' },
  { value: 'BAKERY', label: 'Bakery' },
];

const CHANNEL_OPTIONS = [
  { value: 'POS', label: 'Counter POS' },
  { value: 'KDS', label: 'Kitchen display' },
  { value: 'QR', label: 'Table QR' },
  { value: 'DELIVERY', label: 'Delivery' },
];

const PLAN_OPTIONS = [
  { value: 'STARTER', label: 'Starter' },
  { value: 'PRO', label: 'Professional' },
  { value: 'ENTERPRISE', label: 'Enterprise' },
];

const PERMISSION_OPTIONS = [
  { value: 'INVENTORY_READ', label: 'Read stock levels' },
  { value: 'INVENTORY_WRITE', label: 'Adjust stock levels' },
  { value: 'PRICE_OVERRIDE', label: 'Override unit prices' },
];

export default function InputsStudioPage(): React.JSX.Element {
  const [previewState, setPreviewState] = useState<PreviewState>('default');
  const [copied, setCopied] = useState(false);

  const [itemName, setItemName] = useState('Signature Flat White');
  const [searchQuery, setSearchQuery] = useState('SKU-COF-0042');
  const [notes, setNotes] = useState('Double ristretto, steamed oat milk, 62°C serve temperature.');
  const [unitPrice, setUnitPrice] = useState(() => new Money('4.2000', 'USD'));
  const [safetyStock, setSafetyStock] = useState(12);
  const [wasteAllowance, setWasteAllowance] = useState(15);
  const [managerPin, setManagerPin] = useState('9999');
  const [isTaxable, setIsTaxable] = useState(true);
  const [allowBackorder, setAllowBackorder] = useState(false);
  const [station, setStation] = useState('BARISTA');
  const [channels, setChannels] = useState<readonly string[]>(['POS', 'KDS']);
  const [plan, setPlan] = useState('PRO');
  const [permissions, setPermissions] = useState<readonly string[]>(['INVENTORY_READ']);
  const [openedOn, setOpenedOn] = useState('2026-11-22');
  const [shiftStart, setShiftStart] = useState('08:00');
  const [period, setPeriod] = useState<DateRange>({ startDate: '2026-11-01', endDate: '2026-11-22' });
  const [brandColor, setBrandColor] = useState('#2563EB');
  const [attachment, setAttachment] = useState<File | null>(null);
  const [locale, setLocale] = useState('en');
  const [labels, setLabels] = useState<LocalizedStringMap>({
    en: 'Signature Flat White',
    ar: 'فلات وايت مميز',
    fr: 'Flat White Signature',
  });

  const isDisabled = previewState === 'disabled';
  const errorKey = previewState === 'error' ? 'This value does not satisfy the field constraint.' : undefined;

  const payload = useMemo(
    () => ({
      itemName,
      searchQuery,
      notes,
      unitPrice: { amount: unitPrice.amount, currency: unitPrice.currency },
      safetyStock,
      wasteAllowance: `${wasteAllowance}%`,
      managerPin: '••••',
      isTaxable,
      allowBackorder,
      station,
      channels,
      plan,
      permissions,
      openedOn,
      shiftStart,
      fiscalPeriod: period,
      brandColor,
      attachment: attachment?.name ?? null,
      localizedLabels: labels,
    }),
    [
      itemName,
      searchQuery,
      notes,
      unitPrice,
      safetyStock,
      wasteAllowance,
      isTaxable,
      allowBackorder,
      station,
      channels,
      plan,
      permissions,
      openedOn,
      shiftStart,
      period,
      brandColor,
      attachment,
      labels,
    ]
  );

  return (
    <NexusStack gap="var(--nx-space-6)">
      <NexusStack direction="row" align="center" justify="space-between" style={{ flexWrap: 'wrap', gap: '12px' }}>
        <NexusStack gap="var(--nx-space-1)">
          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            <NexusText variant="h1">Enterprise Input Controls Studio</NexusText>
            <NexusBadge variant="info" label="19 Custom Controls" />
          </NexusStack>
          <NexusText variant="body" role="secondary">
            100% in-house @nexus/ui input primitives with universal Dark/Light parity and zero raw HTML inputs.
          </NexusText>
        </NexusStack>

        <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
          {(['default', 'error', 'disabled'] as const).map((s) => (
            <NexusButton
              key={s}
              variant={previewState === s ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setPreviewState(s)}
            >
              {s.toUpperCase()}
            </NexusButton>
          ))}
        </NexusStack>
      </NexusStack>

      <div className="nx-studio-layout">
        <NexusStack gap="var(--nx-space-6)" style={{ minWidth: 0 }}>
          <StudioTextSection
            itemName={itemName}
            onChangeItemName={setItemName}
            searchQuery={searchQuery}
            onChangeSearchQuery={setSearchQuery}
            notes={notes}
            onChangeNotes={setNotes}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <StudioChoiceSection
            station={station}
            onChangeStation={setStation}
            channels={channels}
            onChangeChannels={setChannels}
            plan={plan}
            onChangePlan={setPlan}
            permissions={permissions}
            onChangePermissions={setPermissions}
            isTaxable={isTaxable}
            onChangeIsTaxable={setIsTaxable}
            allowBackorder={allowBackorder}
            onChangeAllowBackorder={setAllowBackorder}
            stationOptions={STATION_OPTIONS}
            channelOptions={CHANNEL_OPTIONS}
            planOptions={PLAN_OPTIONS}
            permissionOptions={PERMISSION_OPTIONS}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <StudioDateTimeSection
            openedOn={openedOn}
            onChangeOpenedOn={setOpenedOn}
            shiftStart={shiftStart}
            onChangeShiftStart={setShiftStart}
            period={period}
            onChangePeriod={setPeriod}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
          <StudioSpecializedSection
            unitPrice={unitPrice}
            onChangeUnitPrice={setUnitPrice}
            safetyStock={safetyStock}
            onChangeSafetyStock={setSafetyStock}
            wasteAllowance={wasteAllowance}
            onChangeWasteAllowance={setWasteAllowance}
            managerPin={managerPin}
            onChangeManagerPin={setManagerPin}
            brandColor={brandColor}
            onChangeBrandColor={setBrandColor}
            attachment={attachment}
            onChangeAttachment={setAttachment}
            locale={locale}
            onChangeLocale={setLocale}
            labels={labels}
            onChangeLabels={setLabels}
            isDisabled={isDisabled}
            errorKey={errorKey}
          />
        </NexusStack>

        <StudioInspector
          payload={payload}
          previewState={previewState}
        />
      </div>
    </NexusStack>
  );
}
