'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { NexusBadge, NexusStack, NexusText } from '@nexus/ui';
import { NexusGlyph, type GlyphName } from './NexusGlyph';

export interface NexusEnterpriseSidebarProps {
  readonly isOpen?: boolean;
  readonly onNavigate?: () => void;
}

interface NavItem {
  readonly href: string;
  readonly label: string;
  readonly icon: GlyphName;
  readonly hint?: string;
  readonly badge?: string;
  readonly badgeVariant?: 'success' | 'warning' | 'info' | 'neutral';
}

interface NavGroup {
  readonly title: string;
  readonly items: readonly NavItem[];
}

const NAV_GROUPS: readonly NavGroup[] = [
  {
    title: 'Mission Control',
    items: [
      { href: '/', label: 'System Overview', icon: 'dashboard', hint: 'D', badge: 'LIVE', badgeVariant: 'success' },
    ],
  },
  {
    title: 'Commerce & POS',
    items: [
      { href: '/pos', label: 'Counter POS', icon: 'point_of_sale', hint: 'F2' },
      { href: '/kitchen', label: 'Kitchen Display', icon: 'skillet', hint: 'K', badge: '3', badgeVariant: 'warning' },
    ],
  },
  {
    title: 'Inventory & Recipes',
    items: [
      { href: '/inventory', label: 'Recipe BOM & Stock', icon: 'inventory_2', hint: 'N' },
    ],
  },
  {
    title: 'Finance & Treasury',
    items: [
      { href: '/finance', label: 'Shift Cashier Console', icon: 'payments', hint: 'S' },
      { href: '/gateways', label: 'Gateways & Hardware', icon: 'credit_card', hint: 'G', badge: '5', badgeVariant: 'success' },
    ],
  },
  {
    title: 'Workforce & HRMS',
    items: [
      { href: '/hr', label: 'Roster & Punch Clock', icon: 'badge', hint: 'H' },
    ],
  },
  {
    title: 'Ecosystem & Plugins',
    items: [
      { href: '/marketplace', label: 'Feature Marketplace', icon: 'extension', hint: 'M', badge: 'NEW', badgeVariant: 'info' },
    ],
  },
  {
    title: 'SaaS Lifecycle',
    items: [
      { href: '/tenant/lifecycle', label: 'Workspace Governance', icon: 'security', hint: 'W', badge: 'ACTIVE', badgeVariant: 'success' },
      { href: '/register', label: 'Tenant Registration', icon: 'domain_add', hint: 'R' },
      { href: '/onboarding', label: 'Onboarding Wizard', icon: 'storefront', hint: 'O' },
      { href: '/billing', label: 'Subscription & Quotas', icon: 'receipt_long', hint: 'B', badge: 'PRO', badgeVariant: 'neutral' },
    ],
  },
];

export function NexusEnterpriseSidebar({
  isOpen = true,
  onNavigate,
}: NexusEnterpriseSidebarProps): React.JSX.Element {
  const pathname = usePathname();

  return (
    <aside
      className={`nx-sidebar ${isOpen ? '' : 'nx-sidebar--collapsed'}`.trim()}
      aria-label="Primary navigation"
      aria-hidden={!isOpen}
    >
      <nav className="nx-scroll-area" style={{ flex: 1, minHeight: 0, padding: '12px 10px 16px' }}>
        <NexusStack gap="18px">
          {NAV_GROUPS.map((group) => (
            <NexusStack key={group.title} gap="2px">
              <NexusText
                variant="caption"
                role="muted"
                style={{
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  padding: '0 10px 6px',
                  fontSize: '10px',
                  fontWeight: 600,
                }}
              >
                {group.title}
              </NexusText>

              {group.items.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onNavigate}
                    aria-current={isActive ? 'page' : undefined}
                    className={`nx-nav-link ${isActive ? 'nx-nav-link--active' : ''}`.trim()}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '8px',
                      minHeight: '36px',
                      padding: '4px 8px',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      transition: 'background-color 0.12s ease, border-color 0.12s ease',
                    }}
                  >
                    <span style={{ display: 'flex', alignItems: 'center', gap: '9px', minWidth: 0 }}>
                      <span className="nx-nav-icon">
                        <NexusGlyph
                          name={item.icon}
                          size={17}
                          color={isActive ? 'var(--nx-action-primary)' : 'var(--nx-text-muted)'}
                        />
                      </span>
                      <NexusText
                        variant="label"
                        role={isActive ? 'primary' : 'secondary'}
                        style={{
                          fontWeight: isActive ? 600 : 500,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {item.label}
                      </NexusText>
                    </span>

                    {item.badge ? (
                      <NexusBadge variant={item.badgeVariant ?? 'neutral'} label={item.badge} />
                    ) : (
                      item.hint && (
                        <NexusText
                          variant="code"
                          role="muted"
                          style={{
                            fontSize: '10px',
                            padding: '1px 5px',
                            borderRadius: '4px',
                            border: '1px solid var(--nx-border-subtle)',
                          }}
                        >
                          {item.hint}
                        </NexusText>
                      )
                    )}
                  </Link>
                );
              })}
            </NexusStack>
          ))}
        </NexusStack>
      </nav>

      <div
        style={{
          flexShrink: 0,
          padding: '10px 12px 12px',
          borderTop: '1px solid var(--nx-border-subtle)',
          backgroundColor: 'var(--nx-surface-subtle)',
        }}
      >
        <NexusStack gap="6px">
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">ESC/POS Printer</NexusText>
            <NexusBadge variant="success" dot label="Connected" />
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Cash Drawer</NexusText>
            <NexusBadge variant="neutral" label="Armed" />
          </NexusStack>
          <NexusStack direction="row" align="center" justify="space-between">
            <NexusText variant="caption" role="muted">Offline Outbox</NexusText>
            <NexusBadge variant="info" label="0 queued" />
          </NexusStack>
        </NexusStack>
      </div>
    </aside>
  );
}
