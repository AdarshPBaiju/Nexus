'use client';

import React from 'react';
import { NexusBox, NexusText } from '@nexus/ui';

export interface RegisterStepProgressProps {
  readonly currentStep: number;
  readonly totalSteps: number;
}

const STEP_LABELS = [
  'Organization & Region',
  'Operating Vertical',
  'Branch & Currency',
  'Security & Superadmin',
];

export function RegisterStepProgress({
  currentStep,
  totalSteps,
}: RegisterStepProgressProps): React.JSX.Element {
  return (
    <NexusBox
      style={{
        padding: '16px 20px',
        backgroundColor: 'var(--nx-surface-card)',
        borderRadius: '10px',
        border: '1px solid var(--nx-border-default)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
        {STEP_LABELS.map((label, idx) => {
          const stepNum = idx + 1;
          const isDone = stepNum < currentStep;
          const isCurrent = stepNum === currentStep;

          return (
            <div
              key={label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                flex: 1,
                opacity: stepNum > currentStep ? 0.45 : 1,
              }}
            >
              <div
                style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '12px',
                  backgroundColor: isDone || isCurrent ? 'var(--nx-action-primary)' : 'var(--nx-surface-subtle)',
                  color: isDone || isCurrent ? 'var(--nx-action-text)' : 'var(--nx-text-muted)',
                }}
              >
                {isDone ? '✓' : stepNum}
              </div>
              <NexusText
                variant="caption"
                style={{
                  fontWeight: isCurrent ? 700 : 500,
                  color: isCurrent ? 'var(--nx-text-primary)' : 'var(--nx-text-muted)',
                  whiteSpace: 'nowrap',
                }}
              >
                {label}
              </NexusText>
            </div>
          );
        })}
      </div>
    </NexusBox>
  );
}
