'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Navbar(): React.JSX.Element {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Overview' },
    { href: '/pos', label: 'POS Counter' },
    { href: '/kitchen', label: 'KDS Kitchen' },
    { href: '/finance', label: 'Shift Cashier' },
    { href: '/hr', label: 'HR & Staff' },
  ];

  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 24px',
        backgroundColor: 'var(--nx-surface-card)',
        borderBottom: '1px solid var(--nx-border-default)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '-0.5px' }}>
            NEXUS
          </span>
          <span
            style={{
              fontSize: '11px',
              padding: '2px 6px',
              borderRadius: '4px',
              backgroundColor: 'var(--nx-surface-subtle)',
              color: 'var(--nx-text-secondary)',
              fontWeight: 600,
            }}
          >
            v5.4
          </span>
        </Link>

        <nav style={{ display: 'flex', gap: '8px' }}>
          {links.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 500,
                  backgroundColor: isActive ? 'var(--nx-surface-subtle)' : 'transparent',
                  color: isActive ? 'var(--nx-text-primary)' : 'var(--nx-text-secondary)',
                  transition: 'background-color 0.15s',
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 10px',
            borderRadius: '16px',
            backgroundColor: 'var(--nx-surface-subtle)',
            fontSize: '12px',
          }}
        >
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: 'var(--nx-status-success)',
              display: 'inline-block',
            }}
          />
          <span style={{ color: 'var(--nx-text-secondary)' }}>API:8000</span>
        </div>

        <div style={{ fontSize: '12px', color: 'var(--nx-text-muted)' }}>
          Artisan Coffee · WS-LND-01
        </div>
      </div>
    </header>
  );
}
