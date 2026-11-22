'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  NexusBadge,
  NexusBox,
  NexusButton,
  NexusStack,
  NexusText,
} from '@nexus/ui';
import { useAuth } from '../../runtime/auth/AuthContext';

export function Navbar(): React.JSX.Element {
  const pathname = usePathname();
  const { session } = useAuth();

  const links = [
    { href: '/', label: 'Overview' },
    { href: '/pos', label: 'POS Counter' },
    { href: '/kitchen', label: 'KDS Kitchen' },
    { href: '/finance', label: 'Shift Cashier' },
    { href: '/hr', label: 'HR & Staff' },
  ];

  return (
    <NexusBox
      padding="var(--nx-space-3) var(--nx-space-6)"
      style={{
        backgroundColor: 'var(--nx-surface-card)',
        borderBottom: '1px solid var(--nx-border-default)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <NexusStack direction="row" align="center" justify="space-between">
        <NexusStack direction="row" align="center" gap="var(--nx-space-5)">
          <Link href="/">
            <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
              <NexusText variant="h3">NEXUS</NexusText>
              <NexusBadge variant="neutral" label="v5.4" />
            </NexusStack>
          </Link>

          <NexusStack direction="row" align="center" gap="var(--nx-space-2)">
            {links.map((link) => {
              const isActive = pathname === link.href;
              return (
                <Link key={link.href} href={link.href}>
                  <NexusButton
                    variant={isActive ? 'secondary' : 'ghost'}
                    size="sm"
                  >
                    <NexusText
                      variant="label"
                      role={isActive ? 'primary' : 'secondary'}
                    >
                      {link.label}
                    </NexusText>
                  </NexusButton>
                </Link>
              );
            })}
          </NexusStack>
        </NexusStack>

        <NexusStack direction="row" align="center" gap="var(--nx-space-4)">
          <NexusBadge variant="success" label="API: Active" />
          <NexusText variant="caption" role="muted">
            {session.tenantName} · {session.workstationId} ({session.role})
          </NexusText>
        </NexusStack>
      </NexusStack>
    </NexusBox>
  );
}
