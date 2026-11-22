'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { NexusBadge, NexusBox, NexusButton, NexusStack, NexusText } from '@nexus/ui';
import { MarketplaceHeader } from './MarketplaceHeader';
import { PluginCard } from './PluginCard';
import { PluginDetailModal } from './PluginDetailModal';
import type { PluginPackage } from './types';

const CATEGORIES = [
  'All',
  'Commerce',
  'Kitchen Ops',
  'Supply Chain',
  'Finance',
  'Workforce',
  'Hardware',
  'Gaming & Venue',
  'Growth',
] as const;

export default function MarketplacePage(): React.JSX.Element {
  const [plugins, setPlugins] = useState<readonly PluginPackage[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [isBusy, setIsBusy] = useState(false);
  const [detailPlugin, setDetailPlugin] = useState<PluginPackage | null>(null);
  const [notice, setNotice] = useState<{ message: string; variant: 'success' | 'warning' } | null>(null);

  const fetchPlugins = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/plugins');
      if (res.ok) {
        const data = await res.json();
        if (data.plugins) setPlugins(data.plugins);
      }
    } catch {
      // Offline fallback
    }
  }, []);

  useEffect(() => {
    fetchPlugins();
  }, [fetchPlugins]);

  const handleToggle = useCallback(
    async (code: string, action: 'INSTALL' | 'ENABLE' | 'DRAIN' | 'ARCHIVE') => {
      setIsBusy(true);
      try {
        const res = await fetch('/api/v1/plugins/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, action }),
        });
        const data = await res.json();
        if (data.success) {
          setNotice({ message: data.message, variant: action === 'DRAIN' ? 'warning' : 'success' });
          await fetchPlugins();
        } else {
          setNotice({ message: data.error || 'Failed to toggle plugin.', variant: 'warning' });
        }
      } catch {
        setNotice({ message: 'Network error executing plugin command.', variant: 'warning' });
      } finally {
        setIsBusy(false);
      }
    },
    [fetchPlugins]
  );

  const filtered = useMemo(() => {
    return plugins.filter((p) => {
      const matchSearch =
        searchTerm.trim() === '' ||
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchCat = selectedCategory === 'All' || p.category === selectedCategory;
      return matchSearch && matchCat;
    });
  }, [plugins, searchTerm, selectedCategory]);

  const installedCount = useMemo(() => plugins.filter((p) => p.status === 'ACTIVE').length, [plugins]);

  return (
    <div className="nx-page-shell" style={{ maxWidth: '1280px', margin: '0 auto', padding: '24px 20px 48px' }}>
      <NexusStack gap="20px">
        <MarketplaceHeader
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          installedCount={installedCount}
          totalCount={plugins.length}
        />

        {notice && (
          <NexusBox
            style={{
              padding: '12px 16px',
              borderRadius: '8px',
              backgroundColor: notice.variant === 'success' ? 'var(--nx-status-success-subtle, rgba(22, 163, 74, 0.1))' : 'var(--nx-status-warning-subtle, rgba(217, 119, 6, 0.1))',
              border: `1px solid ${notice.variant === 'success' ? 'var(--nx-status-success)' : 'var(--nx-status-warning)'}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <NexusText variant="label" style={{ fontWeight: 600 }}>{notice.message}</NexusText>
            <NexusButton variant="ghost" size="sm" onClick={() => setNotice(null)}>Dismiss</NexusButton>
          </NexusBox>
        )}

        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <NexusButton
                key={cat}
                variant={isSelected ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </NexusButton>
            );
          })}
        </div>

        {filtered.length === 0 ? (
          <NexusBox
            style={{
              padding: '48px 24px',
              textAlign: 'center',
              backgroundColor: 'var(--nx-surface-card)',
              borderRadius: '10px',
              border: '1px solid var(--nx-border-default)',
            }}
          >
            <NexusText variant="h4" role="muted">No Capabilities Found</NexusText>
            <NexusText variant="body" role="muted" style={{ marginTop: '6px' }}>
              No modules matched your search or category filter.
            </NexusText>
          </NexusBox>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
            {filtered.map((plugin) => (
              <PluginCard
                key={plugin.code}
                plugin={plugin}
                onToggle={handleToggle}
                onOpenDetails={setDetailPlugin}
                isBusy={isBusy}
              />
            ))}
          </div>
        )}

        <PluginDetailModal
          plugin={detailPlugin}
          isOpen={detailPlugin !== null}
          onClose={() => setDetailPlugin(null)}
        />
      </NexusStack>
    </div>
  );
}
