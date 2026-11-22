'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth, PRECONFIGURED_STAFF } from '../../runtime/auth/AuthContext';

export function CashierPinLoginScreen(): React.JSX.Element {
  const { activeStaff, selectStaff, loginWithPin } = useAuth();
  const [pin, setPin] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const handleDigit = useCallback((d: string) => {
    setErrorMsg('');
    setPin((prev) => (prev.length < 4 ? prev + d : prev));
  }, []);

  const handleClear = useCallback(() => {
    setPin('');
    setErrorMsg('');
  }, []);

  const handleBackspace = useCallback(() => {
    setPin((prev) => prev.slice(0, -1));
    setErrorMsg('');
  }, []);

  const attemptLogin = useCallback((enteredPin: string) => {
    if (enteredPin.length !== 4) return;
    const ok = loginWithPin(enteredPin);
    if (ok) {
      setIsSuccess(true);
      setErrorMsg('');
    } else {
      setErrorMsg('INVALID PIN — ATTEMPT LOGGED');
      setPin('');
    }
  }, [loginWithPin]);

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
      } else if (e.key === 'Escape' || e.key === 'c' || e.key === 'C') {
        e.preventDefault();
        handleClear();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleDigit, handleBackspace, handleClear]);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center p-4 bg-surface text-on-surface select-none">
      <div className="w-full max-w-md rounded-3xl border border-surface-container-highest bg-surface-container-low p-6 shadow-2xl flex flex-col items-center space-y-5">
        {/* Terminal Header */}
        <div className="flex flex-col items-center space-y-1 text-center">
          <div className="w-12 h-12 rounded-2xl bg-primary/20 text-primary flex items-center justify-center shadow-inner mb-1">
            <span className="material-symbols-outlined text-[28px]">point_of_sale</span>
          </div>
          <h1 className="font-headline-sm text-headline-sm font-bold tracking-tight">NEXUS MISSION CONTROL</h1>
          <p className="text-xs text-outline font-mono">Terminal POS-01 · London SoHo Roastery</p>
        </div>

        {/* Staff Switcher Cards */}
        <div className="grid grid-cols-4 gap-2 w-full">
          {PRECONFIGURED_STAFF.map((staff) => {
            const isSelected = staff.id === activeStaff.id;
            return (
              <button
                key={staff.id}
                type="button"
                onClick={() => { selectStaff(staff.id); handleClear(); }}
                className={`flex flex-col items-center justify-center p-2 rounded-xl border text-center transition-all min-h-[64px] ${
                  isSelected
                    ? 'border-primary bg-primary/10 text-on-surface shadow-sm'
                    : 'border-surface-container-highest bg-surface-container hover:bg-surface-container-high text-outline'
                }`}
              >
                <span className="text-lg">{staff.avatarIcon}</span>
                <span className="text-[11px] font-semibold truncate w-full mt-0.5">{staff.name.split(' ')[0]}</span>
                <span className="text-[9px] font-mono text-outline uppercase">{staff.role.slice(0, 4)}</span>
              </button>
            );
          })}
        </div>

        {/* Active Cashier Status */}
        <div className="text-center space-y-0.5">
          <p className="text-xs text-on-surface-variant font-medium">
            Active Operator: <span className="font-bold text-on-surface">{activeStaff.name}</span>
          </p>
          <p className="text-[11px] text-outline font-mono">
            {activeStaff.title} (PIN: <span className="text-secondary font-bold">{activeStaff.pin}</span>)
          </p>
        </div>

        {/* 4 Secret PIN Dots */}
        <div className="flex items-center gap-4 py-1">
          {[0, 1, 2, 3].map((idx) => {
            const filled = idx < pin.length;
            return (
              <div
                key={idx}
                className={`w-4 h-4 rounded-full border-2 transition-all duration-150 ${
                  filled ? 'border-primary bg-primary scale-110' : 'border-outline/40 bg-transparent'
                }`}
              />
            );
          })}
        </div>

        {/* Status / Error Message */}
        <div className="h-5 text-center">
          {isSuccess ? (
            <span className="text-xs font-mono font-bold text-secondary">AUTHENTICATED — UNLOCKING...</span>
          ) : errorMsg ? (
            <span className="text-xs font-mono font-bold text-error">{errorMsg}</span>
          ) : (
            <span className="text-[11px] font-mono text-outline">Enter 4-digit cashier security PIN</span>
          )}
        </div>

        {/* 10-Key Touch Keypad */}
        <div className="grid grid-cols-3 gap-2.5 w-full max-w-[260px]">
          {['1', '2', '3', '4', '5', '6', '7', '8', '9'].map((digit) => (
            <button
              key={digit}
              type="button"
              onClick={() => handleDigit(digit)}
              className="h-12 rounded-xl bg-surface-container hover:bg-surface-container-high active:scale-95 text-on-surface font-mono text-lg font-bold transition-all shadow-sm flex items-center justify-center cursor-pointer"
            >
              {digit}
            </button>
          ))}
          <button
            type="button"
            onClick={handleClear}
            className="h-12 rounded-xl bg-surface-container hover:bg-surface-container-high active:scale-95 text-outline font-mono text-xs font-bold transition-all flex items-center justify-center cursor-pointer"
          >
            CLR
          </button>
          <button
            type="button"
            onClick={() => handleDigit('0')}
            className="h-12 rounded-xl bg-surface-container hover:bg-surface-container-high active:scale-95 text-on-surface font-mono text-lg font-bold transition-all shadow-sm flex items-center justify-center cursor-pointer"
          >
            0
          </button>
          <button
            type="button"
            onClick={handleBackspace}
            className="h-12 rounded-xl bg-surface-container hover:bg-surface-container-high active:scale-95 text-outline font-mono text-xs font-bold transition-all flex items-center justify-center cursor-pointer"
          >
            ⌫
          </button>
        </div>

        {/* Quick Demo Bypass Hint */}
        <div className="text-[10px] text-outline font-mono text-center pt-1 border-t border-surface-container-highest/60 w-full">
          Touch PIN or use physical Numpad · Auto-submits on 4th digit
        </div>
      </div>
    </div>
  );
}
