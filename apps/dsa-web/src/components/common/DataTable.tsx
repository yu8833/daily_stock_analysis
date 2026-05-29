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
    <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            {selectable && (
              <th className="w-12 px-3 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                <Checkbox
                  checked={isAllSelected}
                  onChange={onSelectAll}
                />
              </th>
            )}
            {columns.map(column => (
              <th
                key={String(column.key)}
                className={`px-3 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${column.width} ${
                  column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                }`}
              >
                {onSort ? (
                  <button
                    type="button"
                    onClick={() => onSort(String(column.key))}
                    className="flex items-center justify-center gap-1 cursor-pointer"
                  >
                    <span>{column.label}</span>
                    {sortField === String(column.key) && (
                      sortOrder === 'asc' ? (
                        <ArrowUp size={14} className="text-blue-500" />
                      ) : (
                        <ArrowDown size={14} className="text-blue-500" />
                      )
                    )}
                  </button>
                ) : (
                  <span>{column.label}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-6 py-12 text-center">
                <EmptyState
                  title={emptyText}
                  description={emptyDescription || ''}
                />
              </td>
            </tr>
          ) : (
            data.map(row => (
              <React.Fragment key={rowKey(row)}>
                <tr className={`hover:bg-gray-50 dark:hover:bg-gray-800 ${rowClassName ? rowClassName(row) : ''}`}>
                  {selectable && (
                    <td className="px-3 py-3">
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

                    return (
                      <td
                        key={String(column.key)}
                        className={`px-3 py-3 text-sm whitespace-nowrap text-gray-900 dark:text-gray-100 ${
                          column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                        } ${cellColor} ${column.type !== 'text' && column.type !== 'flag' ? 'whitespace-nowrap' : ''}`}
                      >
                        {isLinkColumn ? (
                          <a
                            href={getEastMoneyUrl(String(value))}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center gap-1"
                          >
                            {formatCellValue(value, column)}
                            {column.key === 'code' && <ExternalLink size={12} />}
                          </a>
                        ) : column.render ? (
                          column.render(value, row)
                        ) : (
                          formatCellValue(value, column)
                        )}
                      </td>
                    );
                  })}
                </tr>
                {expandedRow && (
                  <tr>
                    <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-6 py-4 bg-blue-50 dark:bg-blue-900/30 border-t border-blue-200 dark:border-blue-800">
                      {expandedRow}
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
