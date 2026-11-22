'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { NexusBadge, NexusBox, NexusStack, NexusText } from '@nexus/ui';

export interface NexusEnterpriseSidebarProps {
  readonly isOpen?: boolean;
}

interface NavItem {
  readonly href: string;
  readonly label: string;
  readonly icon: string;
  readonly badge?: string;
  readonly badgeVariant?: 'success' | 'warning' | 'info' | 'neutral';
}

interface NavGroup {
  readonly title: string;
  readonly items: readonly NavItem[];
}

export function NexusEnterpriseSidebar({
  isOpen = true,
}: NexusEnterpriseSidebarProps): React.JSX.Element {
  const pathname = usePathname();

  const navGroups: readonly NavGroup[] = [
    {
      title: 'MISSION CONTROL',
      items: [
        { href: '/', label: 'System Overview', icon: 'dashboard', badge: 'LIVE', badgeVariant: 'success' },
        { href: '/inputs', label: 'Inputs & Form Studio', icon: 'edit_note', badge: '19 Controls', badgeVariant: 'info' },
      ],
    },
    {
      title: 'COMMERCE & POS',
      items: [
        { href: '/pos', label: 'Counter POS Canvas', icon: 'point_of_sale', badge: 'F4 Pay', badgeVariant: 'neutral' },
        { href: '/kitchen', label: 'KDS Barista Canvas', icon: 'skillet', badge: '3 Orders', badgeVariant: 'warning' },
      ],
    },
    {
      title: 'INVENTORY & RECIPE BOM',
      items: [
        { href: '/inventory', label: 'Recipe BOM & Stock', icon: 'inventory_2', badge: '6 SKUs', badgeVariant: 'info' },
      ],
    },
    {
      title: 'FINANCE & TREASURY',
      items: [
        { href: '/finance', label: 'Shift Cashier Console', icon: 'payments' },
        { href: '/gateways', label: 'Payment Gateways & Rails', icon: 'credit_card', badge: '5 Rails', badgeVariant: 'success' },
      ],
    },
    {
      title: 'WORKFORCE & HRMS',
      items: [
        { href: '/hr', label: 'Staff Roster & Punch Clock', icon: 'badge' },
      ],
    },
    {
      title: 'SAAS LIFECYCLE',
      items: [
        { href: '/billing', label: 'Subscription & Quotas', icon: 'receipt_long', badge: 'PRO', badgeVariant: 'neutral' },
        { href: '/onboarding', label: 'Tenant Onboarding', icon: 'domain_add' },
      ],
    },
  ];

  if (!isOpen) return <></>;

  return (
    <NexusBox
      style={{
        position: 'fixed',
        left: 0,
        top: '56px',
        bottom: 0,
        width: '280px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRight: '1px solid var(--nx-border-default)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        zIndex: 40,
        overflowY: 'auto',
      }}
    >
      <NexusBox padding="var(--nx-space-4)">
        <NexusStack gap="var(--nx-space-4)">
          {navGroups.map((group) => (
            <NexusStack key={group.title} gap="var(--nx-space-1)">
              <NexusText
                variant="caption"
                role="muted"
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '0.05em',
                  paddingLeft: 'var(--nx-space-2)',
                  marginBottom: 'var(--nx-space-1)',
                }}
              >
                {group.title}
              </NexusText>

              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link key={item.href} href={item.href}>
                    <NexusBox
                      padding="7px 12px"
                      style={{
                        borderRadius: '6px',
                        backgroundColor: isActive ? 'var(--nx-surface-subtle)' : 'transparent',
                        border: isActive ? '1px solid var(--nx-border-subtle)' : '1px solid transparent',
                        transition: 'background-color 0.12s ease',
                        cursor: 'pointer',
                      }}
                    >
                      <NexusStack direction="row" align="center" justify="space-between">
                        <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
                          <span
                            className="material-symbols-outlined"
                            style={{
                              fontSize: '18px',
                              color: isActive ? 'var(--nx-action-primary)' : 'var(--nx-text-secondary)',
                            }}
                          >
                            {item.icon}
                          </span>
                          <NexusText
                            variant="label"
                            role={isActive ? 'primary' : 'secondary'}
                            style={{ fontWeight: isActive ? 600 : 500, fontSize: '12px' }}
                          >
                            {item.label}
                          </NexusText>
                        </NexusStack>

                        {item.badge && (
                          <NexusBadge variant={item.badgeVariant ?? 'neutral'} label={item.badge} />
                        )}
                      </NexusStack>
                    </NexusBox>
                  </Link>
                );
              })}
            </NexusStack>
          ))}
        </NexusStack>
      </NexusBox>

      {/* Hardware Telemetry Footer */}
      <NexusBox
        padding="var(--nx-space-3) var(--nx-space-4)"
        style={{
          backgroundColor: 'var(--nx-surface-subtle)',
          borderTop: '1px solid var(--nx-border-default)',
        }}
      >
        <NexusStack gap="var(--nx-space-1)">
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">ESC/POS Printer</NexusText>
            <NexusBadge variant="success" label="Connected" />
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">RJ11 Drawer</NexusText>
            <NexusBadge variant="neutral" label="Armed" />
          </NexusStack>
        </NexusStack>
      </NexusBox>
    </NexusBox>
  );
}
