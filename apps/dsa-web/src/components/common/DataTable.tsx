import React from 'react';
import { Checkbox, EmptyState, Loading } from '../common';
import { ArrowUp, ArrowDown, ExternalLink } from 'lucide-react';
import { formatCellValue, getValueColor, getEastMoneyUrl } from '../../utils/format';
import type { ColumnConfig } from '../../utils/format';

interface DataTableProps<T> {
  columns: ColumnConfig<T>[];
  data: T[];
  loading?: boolean;
  emptyText?: string;
  emptyDescription?: string;
  selectable?: boolean;
  selectedCodes: Set<string>;
  onSelectAll: () => void;
  onSelectRow: (code: string) => void;
  sortField?: string;
  sortOrder?: 'asc' | 'desc';
  onSort?: (field: string) => void;
  linkColumns?: (keyof T)[];
  expandedRow?: React.ReactNode | null;
  rowKey: (row: T) => string;
  rowClassName?: (row: T) => string;
  stickyColumns?: (keyof T)[];
}

export function DataTable<T>({
  columns,
  data,
  loading = false,
  emptyText = '暂无数据',
  emptyDescription,
  selectable = false,
  selectedCodes,
  onSelectAll,
  onSelectRow,
  sortField,
  sortOrder,
  onSort,
  linkColumns = [],
  expandedRow,
  rowKey,
  rowClassName,
  stickyColumns = [],
}: DataTableProps<T>) {
  const isAllSelected = data.length > 0 && selectedCodes.size === data.length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] py-12">
        <Loading label="获取数据中..." />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800 rounded-xl">
      <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
        <thead>
          <tr className="table-header-cell">
            {selectable && (
              <th className="w-14 px-4 py-4 text-center sticky left-0 z-10 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900">
                <Checkbox
                  checked={isAllSelected}
                  onChange={onSelectAll}
                />
              </th>
            )}
            {columns.map(column => {
              const isSticky = stickyColumns.includes(column.key);
              return (
              <th
                key={String(column.key)}
                className={`px-4 py-4 ${column.width} ${
                  column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                } ${isSticky ? 'sticky left-0 z-10 bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900' : ''}`}
              >
                {onSort ? (
                  <button
                    type="button"
                    onClick={() => onSort(String(column.key))}
                    className="flex items-center justify-center gap-2 cursor-pointer hover:text-primary transition-colors duration-200"
                  >
                    <span className="font-semibold">{column.label}</span>
                    {sortField === String(column.key) && (
                      <span className="text-primary">
                        {sortOrder === 'asc' ? (
                          <ArrowUp size={16} />
                        ) : (
                          <ArrowDown size={16} />
                        )}
                      </span>
                    )}
                  </button>
                ) : (
                  <span className="font-semibold">{column.label}</span>
                )}
              </th>
            )})}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-6 py-16 text-center">
                <EmptyState
                  title={emptyText}
                  description={emptyDescription || ''}
                />
              </td>
            </tr>
          ) : (
            data.map((row, index) => (
              <React.Fragment key={rowKey(row)}>
                <tr className={`table-row ${rowClassName ? rowClassName(row) : ''}`} style={{ animationDelay: `${index * 50}ms` }}>
                  {selectable && (
                    <td className="table-cell text-center sticky left-0 z-10 bg-white dark:bg-gray-900">
                      <Checkbox
                        checked={selectedCodes.has(rowKey(row))}
                        onChange={() => onSelectRow(rowKey(row))}
                      />
                    </td>
                  )}
                  {columns.map(column => {
                    const value = row[column.key];
                    const isLinkColumn = linkColumns.includes(column.key);
                    const cellColor = getValueColor(value as number, column.type);
                    const isSticky = stickyColumns.includes(column.key);

                    return (
                      <td
                        key={String(column.key)}
                        className={`table-cell ${
                          column.render ? '' : 'whitespace-nowrap'
                        } ${
                          column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                        } ${cellColor} ${isSticky ? 'sticky left-0 z-10 bg-white dark:bg-gray-900' : ''}`}
                      >
                        {isLinkColumn ? (
                          <a
                            href={getEastMoneyUrl(String(value))}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:text-primary/80 flex items-center gap-1.5 transition-colors duration-200 hover:underline"
                          >
                            <span className="font-medium">{formatCellValue(value, column)}</span>
                            {column.key === 'code' && <ExternalLink size={12} className="opacity-60" />}
                          </a>
                        ) : column.render ? (
                          column.render(value, row)
                        ) : (
                          <span className={`${column.type === 'flag' ? 'font-medium' : ''}`}>
                            {formatCellValue(value, column)}
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
                {expandedRow && (
                  <tr>
                    <td colSpan={columns.length + (selectable ? 1 : 0)} className="bg-gradient-to-r from-blue-50/80 to-cyan-50/80 dark:from-blue-900/40 dark:to-cyan-900/40 border-t border-blue-100 dark:border-blue-800">
                      <div className="px-6 py-4">
                        {expandedRow}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
