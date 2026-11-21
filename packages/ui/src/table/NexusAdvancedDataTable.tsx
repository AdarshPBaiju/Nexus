import React from 'react';
import { BaseListingController } from './BaseListingController';
import { NexusPaginationBar } from './NexusPaginationBar';
import { NexusLoadingSkeleton } from '../feedback/states/NexusLoadingSkeleton';
import { NexusEmptyState } from '../feedback/states/NexusEmptyState';

export interface ColumnDef<TRow> {
  readonly id: string;
  readonly header: string;
  readonly accessor: (row: TRow) => React.ReactNode;
  readonly width?: string;
  readonly isNumeric?: boolean;
}

export interface NexusAdvancedDataTableProps<TRow> {
  readonly controller: BaseListingController<TRow>;
  readonly columns: readonly ColumnDef<TRow>[];
  readonly emptyTitle?: string;
  readonly emptyDescription?: string;
}

export function NexusAdvancedDataTable<TRow>({
  controller,
  columns,
  emptyTitle = 'No Records Found',
  emptyDescription = 'There are no items to display.',
}: NexusAdvancedDataTableProps<TRow>): React.JSX.Element {
  const visibleColumns = columns.filter((col) => controller.visibility.isColumnVisible(col.id));

  if (controller.loading) {
    return <NexusLoadingSkeleton height="200px" />;
  }

  if (controller.data.length === 0) {
    return <NexusEmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', border: '1px solid var(--nx-border-default)', borderRadius: '8px' }}>
      <div style={{ overflowX: 'auto', flex: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }} role="grid">
          <thead>
            <tr style={{ backgroundColor: 'var(--nx-surface-subtle)', borderBottom: '1px solid var(--nx-border-default)' }}>
              {visibleColumns.map((col) => (
                <th key={col.id} style={{ padding: 'var(--nx-space-3) var(--nx-space-4)', width: col.width }}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {controller.data.map((row, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid var(--nx-border-subtle)' }}>
                {visibleColumns.map((col) => (
                  <td key={col.id} style={{ padding: 'var(--nx-space-3) var(--nx-space-4)' }} className={col.isNumeric ? 'nx-numeric' : undefined}>
                    {col.accessor(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <NexusPaginationBar controller={controller.pagination} />
    </div>
  );
}
