/**
 * Multi-Queue Celery & Go Worker Polyglot Contracts.
 */

export const CeleryQueueNames = {
  CRITICAL: 'q.critical',
  DOMAIN: 'q.domain',
  CHANNELS: 'q.channels',
  I18N: 'q.i18n',
  BEAT: 'q.beat',
  MAINTENANCE: 'q.maintenance',
  DEAD_LETTER: 'q.dead_letter',
} as const;

export type CeleryQueueName = (typeof CeleryQueueNames)[keyof typeof CeleryQueueNames];

export const GoWorkerQueues = {
  BATCH: 'go:batch',
} as const;

export type GoWorkerQueue = (typeof GoWorkerQueues)[keyof typeof GoWorkerQueues];

export interface ExportReadyEventDto {
  readonly specversion: '1.0';
  readonly id: string;
  readonly type: 'export.ready.v1';
  readonly source: string;
  readonly data: {
    readonly taskId: string;
    readonly downloadUrl: string;
    readonly byteCount: number;
    readonly expiresAt: string;
  };
}
