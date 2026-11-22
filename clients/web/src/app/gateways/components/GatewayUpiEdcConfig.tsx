'use client';

import React from 'react';
import { NexusBox, NexusButton, NexusSelect, NexusStack, NexusSwitch, NexusText, NexusTextInput } from '@nexus/ui';

export interface UpiEdcConfigData {
  upi_vpa: string;
  upi_merchant_name: string;
  soundbox_paired: boolean;
  edc_protocol: string;
  edc_port: string;
  edc_ip_bridge: string;
}

export interface GatewayUpiEdcConfigProps {
  readonly config: UpiEdcConfigData;
  readonly onChange: (updated: Partial<UpiEdcConfigData>) => void;
  readonly onTestUpi: () => void;
  readonly onTestEdc: () => void;
  readonly isTesting: boolean;
}

export function GatewayUpiEdcConfig({
  config,
  onChange,
  onTestUpi,
  onTestEdc,
  isTesting,
}: GatewayUpiEdcConfigProps): React.JSX.Element {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
      {/* UPI QR & Soundbox Box */}
      <NexusBox
        style={{
          padding: '20px',
          backgroundColor: 'var(--nx-surface-card)',
          borderRadius: '10px',
          border: '1px solid var(--nx-border-default)',
        }}
      >
        <NexusStack gap="14px">
          <div>
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>Direct UPI QR & Soundbox</NexusText>
            <NexusText variant="caption" role="muted">Dynamic POS QR with Instant BLE/Audio Soundbox Confirmation</NexusText>
          </div>
          <NexusTextInput
            labelKey="Merchant VPA Address"
            value={config.upi_vpa}
            onChange={(val: string) => onChange({ upi_vpa: val })}
            placeholderKey="merchant@bankhandle"
          />
          <NexusTextInput
            labelKey="Display Merchant Legal Name"
            value={config.upi_merchant_name}
            onChange={(val: string) => onChange({ upi_merchant_name: val })}
            placeholderKey="Nexus Café Flagship"
          />
          <div style={{ paddingTop: '8px' }}>
            <NexusSwitch
              labelKey="Pair Smart Soundbox via Bluetooth / Webhook"
              value={config.soundbox_paired}
              onChange={(val: boolean) => onChange({ soundbox_paired: val })}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '10px' }}>
            <NexusButton variant="secondary" size="sm" disabled={isTesting} onClick={onTestUpi}>
              Generate Test QR
            </NexusButton>
          </div>
        </NexusStack>
      </NexusBox>

      {/* Local EDC Terminal Bridge Box */}
      <NexusBox
        style={{
          padding: '20px',
          backgroundColor: 'var(--nx-surface-card)',
          borderRadius: '10px',
          border: '1px solid var(--nx-border-default)',
        }}
      >
        <NexusStack gap="14px">
          <div>
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>Serial EDC Terminal Bridge</NexusText>
            <NexusText variant="caption" role="muted">Local USB/Serial Connection to Counter Card Machines</NexusText>
          </div>
          <NexusSelect
            labelKey="Terminal Protocol"
            value={config.edc_protocol}
            onChange={(val: string) => onChange({ edc_protocol: val })}
            options={[
              { value: 'PINE_LABS_PLUTUS', label: 'Pine Labs Plutus (Cloud / Local COM)' },
              { value: 'VERIFONE_VIPA', label: 'Verifone VIPA Serial' },
              { value: 'INGENICO_TELIUM', label: 'Ingenico Telium2 / Tetra' },
            ]}
          />
          <NexusSelect
            labelKey="Hardware Port / Interface"
            value={config.edc_port}
            onChange={(val: string) => onChange({ edc_port: val })}
            options={[
              { value: 'COM1', label: 'Serial COM1' },
              { value: 'COM2', label: 'Serial COM2' },
              { value: 'COM3', label: 'USB Serial COM3 (Auto-Detected)' },
              { value: 'LAN_SOCKET', label: 'TCP/IP Socket Bridge' },
            ]}
          />
          <NexusTextInput
            labelKey="Local IP Bridge Daemon URL"
            value={config.edc_ip_bridge}
            onChange={(val: string) => onChange({ edc_ip_bridge: val })}
            placeholderKey="127.0.0.1:8082"
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '10px' }}>
            <NexusButton variant="secondary" size="sm" disabled={isTesting} onClick={onTestEdc}>
              Poll EDC Terminal
            </NexusButton>
          </div>
        </NexusStack>
      </NexusBox>
    </div>
  );
}
