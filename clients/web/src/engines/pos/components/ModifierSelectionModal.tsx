'use client';

import React, { useId, useState } from 'react';
import type { MenuItemDto, ModifierGroupDto, ModifierOptionDto } from '../catalog.types';

export interface ModifierSelectionModalProps {
  readonly isOpen: boolean;
  readonly item: MenuItemDto;
  readonly onConfirm: (selectedModifiers: readonly ModifierOptionDto[]) => void;
  readonly onCancel: () => void;
}

export const ModifierSelectionModal: React.FC<ModifierSelectionModalProps> = ({
  isOpen,
  item,
  onConfirm,
  onCancel,
}) => {
  const modalLabelId = useId();
  const [selectedMap, setSelectedMap] = useState<Record<string, ModifierOptionDto[]>>({});

  if (!isOpen) return null;

  const groups = item.modifierGroups || [];

  const handleToggle = (group: ModifierGroupDto, opt: ModifierOptionDto) => {
    const current = selectedMap[group.id] || [];
    const isSingle = group.maxSelection === 1;

    if (isSingle) {
      setSelectedMap({ ...selectedMap, [group.id]: [opt] });
      return;
    }

    const exists = current.some((o) => o.id === opt.id);
    if (exists) {
      setSelectedMap({ ...selectedMap, [group.id]: current.filter((o) => o.id !== opt.id) });
    } else if (current.length < group.maxSelection) {
      setSelectedMap({ ...selectedMap, [group.id]: [...current, opt] });
    }
  };

  const isGroupValid = (group: ModifierGroupDto): boolean => {
    const count = (selectedMap[group.id] || []).length;
    return count >= group.minSelection && count <= group.maxSelection;
  };

  const allValid = groups.every(isGroupValid);

  const handleApply = () => {
    if (!allValid) return;
    const flattened = Object.values(selectedMap).flat();
    onConfirm(flattened);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={modalLabelId}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
    >
      <div className="w-full max-w-lg rounded-2xl bg-[var(--nx-surface-elevated)] border border-[var(--nx-border-default)] shadow-2xl p-6 flex flex-col max-h-[85vh]">
        <div className="border-b border-[var(--nx-border-subtle)] pb-4 mb-4">
          <h2 id={modalLabelId} className="text-xl font-bold text-[var(--nx-text-primary)]">
            {item.name}
          </h2>
          <p className="text-sm text-[var(--nx-text-secondary)]">
            Base: {item.currency} {item.basePrice} · Customize preparation
          </p>
        </div>

        <div className="flex-1 overflow-y-auto space-y-6 pr-1">
          {groups.map((group) => {
            const current = selectedMap[group.id] || [];
            const valid = isGroupValid(group);
            return (
              <div key={group.id} className="space-y-3">
                <div className="flex justify-between items-center">
                  <h3 className="font-semibold text-sm text-[var(--nx-text-primary)]">
                    {group.name}
                    {group.isRequired && (
                      <span className="text-[var(--nx-status-danger)] ml-1">*</span>
                    )}
                  </h3>
                  <span className={`text-xs ${valid ? 'text-[var(--nx-text-muted)]' : 'text-[var(--nx-status-danger)]'}`}>
                    Select {group.minSelection === group.maxSelection ? group.minSelection : `${group.minSelection}–${group.maxSelection}`}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {group.options.map((opt) => {
                    const isSelected = current.some((o) => o.id === opt.id);
                    return (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => handleToggle(group, opt)}
                        className={`min-h-[44px] px-3 py-2 rounded-xl text-left border text-sm transition-all flex justify-between items-center ${
                          isSelected
                            ? 'bg-[var(--nx-surface-selected)] border-[var(--nx-border-focus)] text-[var(--nx-text-primary)] font-medium'
                            : 'bg-[var(--nx-surface-subtle)] border-[var(--nx-border-subtle)] text-[var(--nx-text-secondary)] hover:border-[var(--nx-border-default)]'
                        }`}
                      >
                        <span className="truncate">{opt.name}</span>
                        {Number(opt.priceDelta) > 0 && (
                          <span className="text-xs font-semibold text-[var(--nx-text-muted)] ml-1">
                            +{opt.priceDelta}
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 pt-4 border-t border-[var(--nx-border-subtle)] flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 min-h-[44px] rounded-xl border border-[var(--nx-border-default)] bg-[var(--nx-surface-subtle)] text-[var(--nx-text-primary)] font-medium hover:bg-[var(--nx-surface-card)]"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={!allValid}
            onClick={handleApply}
            className="flex-1 min-h-[44px] rounded-xl bg-[var(--nx-action-primary)] text-[var(--nx-action-text)] font-semibold shadow disabled:opacity-40 disabled:cursor-not-allowed hover:bg-[var(--nx-action-primary-hover)]"
          >
            Add to Order
          </button>
        </div>
      </div>
    </div>
  );
};
