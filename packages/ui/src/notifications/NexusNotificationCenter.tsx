'use client';
import React, { useState } from 'react';

export interface NotificationItem {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly category: 'ALL' | 'ORDERS' | 'SYSTEM';
  readonly isRead: boolean;
  readonly createdAt: string;
  readonly actionUrl?: string;
}

export interface NexusNotificationCenterProps {
  readonly notifications: readonly NotificationItem[];
  readonly onMarkAsRead?: (id: string) => void;
  readonly onMarkAllAsRead?: () => void;
  readonly onActionClick?: (url: string) => void;
}

/**
 * Universal accessible notification center panel with dual-mode theme parity.
 */
export const NexusNotificationCenter: React.FC<NexusNotificationCenterProps> = ({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
  onActionClick,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<'ALL' | 'ORDERS' | 'SYSTEM'>('ALL');

  const filtered = notifications.filter(
    (item) => selectedCategory === 'ALL' || item.category === selectedCategory
  );

  const unreadCount = notifications.filter((item) => !item.isRead).length;

  return (
    <div className="w-80 md:w-96 rounded-lg border border-[var(--nx-border-default)] bg-[var(--nx-surface-card)] text-[var(--nx-text-primary)] shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-[var(--nx-border-subtle)] bg-[var(--nx-surface-subtle)]">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm">Notifications</span>
          {unreadCount > 0 && (
            <span className="px-1.5 py-0.5 text-xs font-bold rounded-full bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] nx-numeric">
              {unreadCount}
            </span>
          )}
        </div>
        {unreadCount > 0 && onMarkAllAsRead && (
          <button
            type="button"
            onClick={onMarkAllAsRead}
            className="text-xs text-[var(--nx-action-primary)] hover:underline focus:outline-none"
          >
            Mark all read
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-[var(--nx-border-subtle)] bg-[var(--nx-surface-card)] text-xs">
        {(['ALL', 'ORDERS', 'SYSTEM'] as const).map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setSelectedCategory(cat)}
            className={`flex-1 py-2 text-center transition-colors ${
              selectedCategory === cat
                ? 'border-b-2 border-[var(--nx-border-focus)] font-medium text-[var(--nx-text-primary)]'
                : 'text-[var(--nx-text-secondary)] hover:text-[var(--nx-text-primary)]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Items List */}
      <div className="max-h-80 overflow-y-auto divide-y divide-[var(--nx-border-subtle)]">
        {filtered.length === 0 ? (
          <div className="p-6 text-center text-xs text-[var(--nx-text-muted)]">
            No notifications in this category
          </div>
        ) : (
          filtered.map((item) => (
            <div
              key={item.id}
              className={`p-3 transition-colors ${
                item.isRead ? 'opacity-75' : 'bg-[var(--nx-surface-selected)]/10 font-medium'
              }`}
            >
              <div className="flex justify-between items-start gap-2">
                <span className="text-xs font-semibold text-[var(--nx-text-primary)]">
                  {item.title}
                </span>
                <span className="text-[10px] text-[var(--nx-text-muted)] nx-numeric">
                  {item.createdAt}
                </span>
              </div>
              <p className="mt-1 text-xs text-[var(--nx-text-secondary)] line-clamp-2">
                {item.body}
              </p>
              <div className="mt-2 flex items-center justify-between text-xs">
                {item.actionUrl && onActionClick && (
                  <button
                    type="button"
                    onClick={() => onActionClick(item.actionUrl!)}
                    className="text-[var(--nx-action-primary)] hover:underline"
                  >
                    View details
                  </button>
                )}
                {!item.isRead && onMarkAsRead && (
                  <button
                    type="button"
                    onClick={() => onMarkAsRead(item.id)}
                    className="text-[10px] text-[var(--nx-text-muted)] hover:text-[var(--nx-text-primary)] ml-auto"
                  >
                    Mark read
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
