'use client';

import React from 'react';
import {
  NexusBox,
  NexusButton,
  NexusNumberInput,
  NexusSelect,
  NexusStack,
  NexusSwitch,
  NexusText,
  NexusTextInput,
} from '@nexus/ui';

export interface PrinterHardwareConfigData {
  kitchen_ip: string;
  kitchen_port: number;
  kitchen_cutter: boolean;
  barista_ip: string;
  counter_interface: string;
  drawer_port: string;
  drawer_pulse_ms: number;
  drawer_auto_kick: boolean;
}

export interface GatewayPrinterHardwareConfigProps {
  readonly config: PrinterHardwareConfigData;
  readonly onChange: (updated: Partial<PrinterHardwareConfigData>) => void;
  readonly onTestPrint: (printerName: string) => void;
  readonly onKickDrawer: () => void;
  readonly isTesting: boolean;
}

export function GatewayPrinterHardwareConfig({
  config,
  onChange,
  onTestPrint,
  onKickDrawer,
  isTesting,
}: GatewayPrinterHardwareConfigProps): React.JSX.Element {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '16px' }}>
      {/* Kitchen & Barista Thermal ESC/POS */}
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
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>
              Kitchen & Barista ESC/POS Printers
            </NexusText>
            <NexusText variant="caption" role="muted">
              Raw Network Socket (Port 9100) Direct Thermal Printing
            </NexusText>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '10px' }}>
            <NexusTextInput
              labelKey="Kitchen KDS Thermal IP"
              value={config.kitchen_ip}
              onChange={(val: string) => onChange({ kitchen_ip: val })}
              placeholderKey="192.168.1.180"
            />
            <NexusNumberInput
              labelKey="Port"
              value={config.kitchen_port}
              onChange={(val: number | null) => onChange({ kitchen_port: val ?? 9100 })}
            />
          </div>
          <NexusTextInput
            labelKey="Barista Station Thermal IP"
            value={config.barista_ip}
            onChange={(val: string) => onChange({ barista_ip: val })}
            placeholderKey="192.168.1.181"
          />
          <NexusSwitch
            labelKey="Auto-Cut Paper on Ticket End"
            value={config.kitchen_cutter}
            onChange={(val: boolean) => onChange({ kitchen_cutter: val })}
          />
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', paddingTop: '10px' }}>
            <NexusButton
              variant="secondary"
              size="sm"
              disabled={isTesting}
              onClick={() => onTestPrint('Kitchen Bixolon 80mm')}
            >
              Print Test Ticket
            </NexusButton>
          </div>
        </NexusStack>
      </NexusBox>

      {/* Cash Drawer & Receipt Printer */}
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
            <NexusText variant="h4" style={{ margin: 0, fontWeight: 700 }}>
              Cashier Receipt & RJ11 Drawer
            </NexusText>
            <NexusText variant="caption" role="muted">
              High-Speed USB Printer & Solenoid Drawer Kick
            </NexusText>
          </div>
          <NexusSelect
            labelKey="Counter Receipt Interface"
            value={config.counter_interface}
            onChange={(val: string) => onChange({ counter_interface: val })}
            options={[
              { value: 'USB-HID', label: 'USB Direct (Star Micronics TSP143 / Epson TM-T88)' },
              { value: 'SERIAL_COM', label: 'Legacy RS-232 Serial Port' },
              { value: 'LAN_SOCKET', label: 'Ethernet Direct 9100' },
            ]}
          />
          <NexusTextInput
            labelKey="Cash Drawer Port Binding"
            value={config.drawer_port}
            onChange={(val: string) => onChange({ drawer_port: val })}
            placeholderKey="RJ11 Solenoid via Printer 1"
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', alignItems: 'center' }}>
            <NexusNumberInput
              labelKey="Pulse Duration (ms)"
              value={config.drawer_pulse_ms}
              onChange={(val: number | null) => onChange({ drawer_pulse_ms: val ?? 100 })}
            />
            <div style={{ paddingTop: '18px' }}>
              <NexusSwitch
                labelKey="Auto-Kick on Cash"
                value={config.drawer_auto_kick}
                onChange={(val: boolean) => onChange({ drawer_auto_kick: val })}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end', paddingTop: '10px' }}>
            <NexusButton variant="secondary" size="sm" disabled={isTesting} onClick={onKickDrawer}>
              Kick Drawer Test
            </NexusButton>
          </div>
        </NexusStack>
      </NexusBox>
    </div>
  );
}
