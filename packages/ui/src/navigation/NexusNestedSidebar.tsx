'use client';
import React, { useState } from 'react';
import { NavItem } from './types';
import { NexusText } from '../typography/NexusText';
import { NexusIcon } from '../icons/NexusIcon';

export interface NexusNestedSidebarProps {
  readonly items: readonly NavItem[];
  readonly activeId?: string;
  readonly isCollapsed?: boolean;
}

export function NexusNestedSidebar({
  items,
  activeId,
  isCollapsed = false,
}: NexusNestedSidebarProps): React.JSX.Element {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpand = (id: string) => {
    const next = new Set(expandedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedIds(next);
  };

  return (
    <nav
      style={{
        width: isCollapsed ? '64px' : '260px',
        backgroundColor: 'var(--nx-surface-subtle)',
        borderInlineEnd: '1px solid var(--nx-border-default)',
        height: '100%',
        overflowY: 'auto',
        padding: 'var(--nx-space-2)',
        transition: 'width 0.2s ease',
      }}
      aria-label="Sidebar Navigation"
    >
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
        {items.map((item) => {
          const isActive = item.id === activeId;
          const isExpanded = expandedIds.has(item.id);
          const hasChildren = item.children && item.children.length > 0;

          return (
            <li key={item.id}>
              <div
                onClick={() => (hasChildren ? toggleExpand(item.id) : null)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: 'var(--nx-space-2) var(--nx-space-3)',
                  borderRadius: '6px',
                  backgroundColor: isActive ? 'var(--nx-surface-selected)' : 'transparent',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--nx-space-2)' }}>
                  <NexusIcon name="chevron-right" size="sm" />
                  {!isCollapsed && <NexusText variant="body">{item.label}</NexusText>}
                </div>
                {hasChildren && !isCollapsed && (
                  <NexusIcon name={isExpanded ? 'chevron-down' : 'chevron-right'} size="sm" />
                )}
              </div>
              {hasChildren && isExpanded && !isCollapsed && (
                <ul style={{ listStyle: 'none', paddingInlineStart: 'var(--nx-space-4)', margin: '4px 0 0 0' }}>
                  {item.children!.map((child) => (
                    <li key={child.id} style={{ padding: '4px 8px' }}>
                      <NexusText variant="caption">{child.label}</NexusText>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
