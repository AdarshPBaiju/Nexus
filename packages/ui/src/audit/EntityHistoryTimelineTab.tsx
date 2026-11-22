import React from 'react';

export interface AuditTimelineItem {
  id: string;
  timestamp: string;
  eventType: string;
  actorName: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  outcome: 'SUCCESS' | 'DENIED' | 'FAILED';
  changedCount: number;
}

export interface EntityHistoryTimelineTabProps {
  items: AuditTimelineItem[];
  onSelectEvent?: (item: AuditTimelineItem) => void;
}

export const EntityHistoryTimelineTab: React.FC<EntityHistoryTimelineTabProps> = ({
  items,
  onSelectEvent,
}) => {
  if (items.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-[var(--nx-text-muted)] italic">
        No audit activity recorded for this entity.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-3 font-sans">
      {items.map((item) => (
        <div
          key={item.id}
          onClick={() => onSelectEvent?.(item)}
          className="flex items-center justify-between p-3 rounded border border-[var(--nx-border-subtle)] bg-[var(--nx-surface-card)] hover:bg-[var(--nx-surface-subtle)] cursor-pointer transition-colors"
        >
          <div className="flex items-center space-x-3">
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                item.severity === 'CRITICAL'
                  ? 'bg-rose-500'
                  : item.severity === 'WARNING'
                  ? 'bg-amber-500'
                  : 'bg-blue-500'
              }`}
            />
            <div>
              <div className="text-sm font-medium text-[var(--nx-text-primary)]">
                {item.eventType}
              </div>
              <div className="text-xs text-[var(--nx-text-secondary)]">
                By {item.actorName} · {item.timestamp}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 text-xs">
            <span className="px-2 py-0.5 rounded bg-[var(--nx-surface-subtle)] text-[var(--nx-text-secondary)]">
              {item.changedCount} field(s) changed
            </span>
            <span
              className={`px-2 py-0.5 rounded font-semibold ${
                item.outcome === 'SUCCESS'
                  ? 'text-emerald-700 bg-emerald-500/10'
                  : 'text-rose-700 bg-rose-500/10'
              }`}
            >
              {item.outcome}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
