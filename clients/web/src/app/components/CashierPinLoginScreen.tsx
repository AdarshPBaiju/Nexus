'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { NexusBadge, NexusStack, NexusText } from '@nexus/ui';
import { useAuth, PRECONFIGURED_STAFF } from '../../runtime/auth/AuthContext';
import { NexusGlyph } from './NexusGlyph';
import { StaffProfileRow } from './auth/StaffProfileRow';
import { PinKeypad } from './auth/PinKeypad';

export function CashierPinLoginScreen(): React.JSX.Element {
  const { activeStaff, selectStaff, loginWithPin } = useAuth();
  const [pin, setPin] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleDigit = useCallback((digit: string) => {
    setErrorMsg('');
    setPin((prev) => (prev.length < 4 ? prev + digit : prev));
  }, []);

  const handleClear = useCallback(() => {
    setPin('');
    setErrorMsg('');
  }, []);

  const handleBackspace = useCallback(() => {
    setPin((prev) => prev.slice(0, -1));
    setErrorMsg('');
  }, []);

  const attemptLogin = useCallback(
    async (enteredPin: string) => {
      if (enteredPin.length !== 4) return;
      const ok = await loginWithPin(enteredPin);
      if (ok) {
        setIsSuccess(true);
        setErrorMsg('');
      } else {
        setErrorMsg('Incorrect PIN — attempt has been logged.');
        setPin('');
      }
    },
    [loginWithPin]
  );

  useEffect(() => {
    if (pin.length === 4) {
      attemptLogin(pin);
    }
  }, [pin, attemptLogin]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (/^[0-9]$/.test(e.key)) {
        e.preventDefault();
        handleDigit(e.key);
      } else if (e.key === 'Backspace') {
        e.preventDefault();
        handleBackspace();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        handleClear();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleDigit, handleBackspace, handleClear]);

  return (
    <div
      style={{
        minHeight: '100dvh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        backgroundColor: 'var(--nx-surface-bg)',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '420px',
          borderRadius: '12px',
          border: '1px solid var(--nx-border-default)',
          backgroundColor: 'var(--nx-surface-card)',
          boxShadow: '0 24px 70px -30px rgba(0, 0, 0, 0.55)',
          padding: '22px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        <NexusStack align="center" gap="6px">
          <span
            aria-hidden="true"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'var(--nx-action-primary)',
            }}
          >
            <NexusGlyph name="point_of_sale" size={22} color="var(--nx-action-text)" />
          </span>
          <NexusText variant="h3">Sign in to this terminal</NexusText>
          <NexusText variant="caption" role="muted" style={{ textAlign: 'center' }}>
            {activeStaff.tenantName} · {activeStaff.branchName} · {activeStaff.workstationId}
          </NexusText>
        </NexusStack>

        <StaffProfileRow
          staffList={PRECONFIGURED_STAFF}
          activeStaffId={activeStaff.id}
          onSelectStaff={(id) => {
            selectStaff(id);
            handleClear();
          }}
        />

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            borderRadius: '8px',
            backgroundColor: 'var(--nx-surface-subtle)',
            border: '1px solid var(--nx-border-subtle)',
          }}
        >
          <NexusText variant="caption" role="muted">Operator</NexusText>
          <NexusText variant="label">{activeStaff.title}</NexusText>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', padding: '2px 0' }}>
          {[0, 1, 2, 3].map((idx) => {
            const filled = idx < pin.length;
            return (
              <span
                key={idx}
                aria-hidden="true"
                style={{
                  width: '13px',
                  height: '13px',
                  borderRadius: '9999px',
                  border: `2px solid ${filled ? 'var(--nx-action-primary)' : 'var(--nx-border-default)'}`,
                  backgroundColor: filled ? 'var(--nx-action-primary)' : 'transparent',
                  transition: 'background-color 0.12s ease',
                }}
              />
            );
          })}
        </div>

        <div style={{ minHeight: '18px', textAlign: 'center' }}>
          {isSuccess ? (
            <NexusBadge variant="success" dot label="Authenticated — unlocking session" />
          ) : errorMsg ? (
            <NexusText variant="caption" style={{ color: 'var(--nx-status-danger-text)', fontWeight: 600 }}>
              {errorMsg}
            </NexusText>
          ) : (
            <NexusText variant="caption" role="muted">Enter your 4-digit cashier PIN</NexusText>
          )}
        </div>

        <PinKeypad onDigit={handleDigit} onClear={handleClear} onBackspace={handleBackspace} />

        <NexusText variant="caption" role="muted" style={{ textAlign: 'center', fontSize: '10px' }}>
          Hardware numpad supported · Session restores after refresh until you lock the terminal
        </NexusText>
      </div>
    </div>
  );
}
