import type { Metadata } from 'next';
import './globals.css';
import React from 'react';
import { AuthProvider } from '../runtime/auth/AuthContext';
import { NexusAppChrome } from './components/NexusAppChrome';

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
          <NexusAppChrome>{children}</NexusAppChrome>
        </AuthProvider>
      </body>
    </html>
  );
}
