import type { Metadata } from 'next';
import './globals.css';
import React from 'react';
import { AuthProvider } from '../runtime/auth/AuthContext';
import { NexusShellRoot } from './components/NexusShellRoot';
import { NexusBox } from '@nexus/ui';

export const metadata: Metadata = {
  title: 'Project Nexus — Mission Control & Enterprise Operating System',
  description: 'Enterprise Financial, Venue, POS, KDS & Workforce Operating System',
};

export default function RootLayout({
  children,
}: {
  readonly children: React.ReactNode;
}): React.JSX.Element {
  return (
    <html lang="en" data-theme="dark">
      <body>
        <AuthProvider>
          <NexusShellRoot>
            <NexusBox style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              {children}
            </NexusBox>
          </NexusShellRoot>
        </AuthProvider>
      </body>
    </html>
  );
}
