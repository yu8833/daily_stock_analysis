import React, { useMemo } from 'react';
import { Checkbox, EmptyState, Loading } from '../common';
import { ArrowUp, ArrowDown, ExternalLink } from 'lucide-react';
import { formatCellValue, getValueColor, getEastMoneyUrl } from '../../utils/format';
import type { ColumnConfig, ColumnGroup } from '../../utils/format';

interface DataTableProps<T> {
  columns: ColumnConfig<T>[];
  groups?: ColumnGroup[];
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
  flagFilters?: Record<string, string>;
  onFlagFilterChange?: (key: string, value: string) => void;
}

export function DataTable<T>({
  columns,
  groups = [],
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
  flagFilters = {},
  onFlagFilterChange,
}: DataTableProps<T>) {
  const { groupedColumns } = useMemo(() => {
    if (groups.length === 0) {
      return { groupedColumns: [] };
    }

    const groupMap = new Map<string, typeof columns>();
    const ungrouped: typeof columns = [];

    for (const col of columns) {
      if (col.group && groups.some(g => g.id === col.group)) {
        if (!groupMap.has(col.group)) {
          groupMap.set(col.group, []);
        }
        groupMap.get(col.group)!.push(col);
      } else {
        ungrouped.push(col);
      }
    }

    const result: Array<{ group: ColumnGroup; columns: typeof columns }> = [];
    for (const g of groups) {
      if (groupMap.has(g.id)) {
        result.push({ group: g, columns: groupMap.get(g.id)! });
      }
    }

    if (ungrouped.length > 0) {
      result.push({ group: { id: 'other', label: '其他' }, columns: ungrouped });
    }

    return { groupedColumns: result };
  }, [columns, groups]);

  // 计算每个sticky列的left位置
  const stickyPositionMap = useMemo(() => {
    const map = new Map<keyof T, number>();
    let leftOffset = selectable ? 56 : 0; // 选择框列宽度
    
    for (const colKey of stickyColumns) {
      const col = columns.find(c => c.key === colKey);
      if (col) {
        map.set(colKey, leftOffset);
        const widthMatch = col.width.match(/w-(\d+)/);
        if (widthMatch) {
          const wValue = parseInt(widthMatch[1]);
          leftOffset += wValue * 4;
        } else {
          leftOffset += 80;
        }
      }
    }
    return map;
  }, [stickyColumns, columns, selectable]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] py-12">
        <Loading label="获取数据中..." />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px] py-12">
        <EmptyState title={emptyText} description={emptyDescription || ''} />
      </div>
    );
  }

  if (groupedColumns.length === 0) {
    return (
      <div className="relative h-[600px]">
        <div className="overflow-x-auto overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800 rounded-xl h-full">
          <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
            <thead className="sticky top-0 z-20 bg-gray-50 dark:bg-gray-800 shadow-sm">
              <tr className="table-header-cell">
                {selectable && (
                  <th className="w-14 px-4 py-3 text-center sticky left-0 z-30 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
                    <Checkbox checked={selectedCodes.size === data.length && data.length > 0} onChange={onSelectAll} />
                  </th>
                )}
                {columns.map(column => {
                  const isSticky = stickyColumns.includes(column.key);
                  const isFlagColumn = column.type === 'flag';
                  const columnKey = String(column.key);
                  const currentFilter = flagFilters[columnKey] || '';
                  const leftPosition = stickyPositionMap.get(column.key);

                  return (
                    <th
                      key={columnKey}
                      className={`px-2 py-3 ${column.width} text-xs whitespace-nowrap ${
                        column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                      } border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 ${isSticky ? 'sticky z-30 border-r border-gray-200 dark:border-gray-700' : ''}`}
                      style={isSticky && leftPosition !== undefined ? { left: `${leftPosition}px` } : {}}
                    >
                      <div className="flex items-center justify-center gap-1">
                        {onSort && !isFlagColumn ? (
                          <button
                            type="button"
                            onClick={() => onSort(columnKey)}
                            className="flex items-center justify-center gap-1 cursor-pointer hover:text-primary transition-colors duration-200"
                          >
                            <span className="font-semibold">{column.label}</span>
                            {sortField === columnKey && (
                              <span className="text-primary">
                                {sortOrder === 'asc' ? (
                                  <ArrowUp size={12} />
                                ) : (
                                  <ArrowDown size={12} />
                                )}
                              </span>
                            )}
                          </button>
                        ) : (
                          <span className="font-semibold">{column.label}</span>
                        )}
                      </div>
                      {isFlagColumn && onFlagFilterChange && (
                        <div className="flex justify-center mt-1">
                          <select
                            value={currentFilter}
                            onChange={(e) => onFlagFilterChange(columnKey, e.target.value)}
                            className="px-1 py-0.5 text-xs bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                          >
                            <option value="">全部</option>
                            <option value="是">是</option>
                            <option value="否">否</option>
                            <option value="-">-</option>
                          </select>
                        </div>
                      )}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900">
              {data.map((row, index) => (
                <React.Fragment key={rowKey(row)}>
                  <tr className={`table-row ${rowClassName ? rowClassName(row) : ''}`} style={{ animationDelay: `${index * 50}ms` }}>
                    {selectable && (
                      <td className="table-cell text-center sticky left-0 z-10 bg-white dark:bg-gray-900">
                        <Checkbox checked={selectedCodes.has(rowKey(row))} onChange={() => onSelectRow(rowKey(row))} />
                      </td>
                    )}
                    {columns.map(column => {
                      const value = row[column.key];
                      const isLinkColumn = linkColumns.includes(column.key);
                      const cellColor = getValueColor(value as number, column.type);
                      const isSticky = stickyColumns.includes(column.key);
                      const leftPosition = stickyPositionMap.get(column.key);

                      return (
                        <td
                          key={String(column.key)}
                          className={`table-cell ${column.width} ${
                            column.render ? '' : 'whitespace-nowrap'
                          } ${
                            column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                          } ${cellColor} border-b border-gray-100 dark:border-gray-800 ${isSticky ? 'sticky z-10 bg-white dark:bg-gray-900' : ''}`}
                          style={isSticky && leftPosition !== undefined ? { left: `${leftPosition}px` } : {}}
                        >
                          {isLinkColumn ? (
                            <a
                              href={getEastMoneyUrl(String(column.key === 'code' ? value : (row as { code: string }).code))}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary hover:text-primary/80 flex items-center gap-1 transition-colors duration-200 hover:underline whitespace-nowrap"
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
                  {expandedRow && selectedCodes.has(rowKey(row)) && (
                    <tr key={`${rowKey(row)}-expanded`}>
                      <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-4 py-4 bg-gray-50 dark:bg-gray-800">
                        {expandedRow}
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-[600px]">
      <div className="overflow-x-auto overflow-y-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800 rounded-xl h-full">
        <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
          <thead className="sticky top-0 z-20 bg-gray-50 dark:bg-gray-800 shadow-sm">
            <tr>
              {selectable && (
                <th className="w-14 px-4 py-2 text-center sticky left-0 z-40 bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700" rowSpan={2}>
                  <Checkbox checked={selectedCodes.size === data.length && data.length > 0} onChange={onSelectAll} />
                </th>
              )}
              {groupedColumns.map((groupInfo, groupIndex) => {
                const isFirstGroup = groupIndex === 0;
                const isLastGroup = groupIndex === groupedColumns.length - 1;
                const hasSticky = groupInfo.columns.some(col => stickyColumns.includes(col.key));
                

                return (
                  <th
                    key={groupInfo.group.id}
                    colSpan={groupInfo.columns.length}
                    className={`px-2 py-2 text-center border-b-2 border-x border-gray-200 dark:border-gray-700 bg-gradient-to-r from-gray-100 to-gray-50 dark:from-gray-700 dark:to-gray-800 ${isFirstGroup ? 'border-l-2' : ''} ${isLastGroup ? 'border-r-2' : ''} ${isFirstGroup && hasSticky ? 'sticky z-40' : ''}`}
                    style={isFirstGroup && hasSticky ? { left: selectable ? '56px' : '0' } : {}}
                  >
                    <span className="font-bold text-sm">{groupInfo.group.label}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400"> ({groupInfo.columns.length}项)</span>
                  </th>
                );
              })}
            </tr>
            <tr>
              {groupedColumns.map((groupInfo, groupIndex) => {
                const isFirstGroup = groupIndex === 0;
                const isLastGroup = groupIndex === groupedColumns.length - 1;

                return groupInfo.columns.map((column, colIndex) => {
                  const isFirstColumn = colIndex === 0;
                  const isFlagColumn = column.type === 'flag';
                  const columnKey = String(column.key);
                  const currentFilter = flagFilters[columnKey] || '';
                  const isSticky = stickyColumns.includes(column.key);
                  const leftPosition = stickyPositionMap.get(column.key);

                  return (
                    <th
                      key={columnKey}
                      className={`px-2 py-2 ${column.width} text-xs whitespace-nowrap ${
                        column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                      } border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 ${isFirstGroup && isFirstColumn ? 'border-l-2' : ''} ${isLastGroup && colIndex === groupInfo.columns.length - 1 ? 'border-r-2' : ''} ${isFirstColumn ? 'border-l' : ''} ${isSticky ? 'sticky z-30 border-r border-gray-200 dark:border-gray-700' : ''}`}
                      style={isSticky && leftPosition !== undefined ? { left: `${leftPosition}px` } : {}}
                    >
                      <div className="flex items-center justify-center gap-1">
                        {onSort && !isFlagColumn ? (
                          <button
                            type="button"
                            onClick={() => onSort(columnKey)}
                            className="flex items-center justify-center gap-1 cursor-pointer hover:text-primary transition-colors duration-200"
                          >
                            <span className="font-semibold">{column.label}</span>
                            {sortField === columnKey && (
                              <span className="text-primary">
                                {sortOrder === 'asc' ? (
                                  <ArrowUp size={10} />
                                ) : (
                                  <ArrowDown size={10} />
                                )}
                              </span>
                            )}
                          </button>
                        ) : (
                          <span className="font-semibold">{column.label}</span>
                        )}
                      </div>
                      {isFlagColumn && onFlagFilterChange && (
                        <div className="flex justify-center mt-1">
                          <select
                            value={currentFilter}
                            onChange={(e) => onFlagFilterChange(columnKey, e.target.value)}
                            className="px-1 py-0.5 text-xs bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                          >
                            <option value="">全部</option>
                            <option value="是">是</option>
                            <option value="否">否</option>
                            <option value="-">-</option>
                          </select>
                        </div>
                      )}
                    </th>
                  );
                });
              })}
            </tr>
          </thead>
          
          <tbody className="bg-white dark:bg-gray-900">
            {data.map((row, index) => (
              <React.Fragment key={rowKey(row)}>
                <tr className={`table-row ${rowClassName ? rowClassName(row) : ''}`} style={{ animationDelay: `${index * 50}ms` }}>
                  {selectable && (
                    <td className="table-cell text-center sticky left-0 z-20 bg-white dark:bg-gray-900 border-r border-gray-100 dark:border-gray-800">
                      <Checkbox
                        checked={selectedCodes.has(rowKey(row))}
                        onChange={() => onSelectRow(rowKey(row))}
                      />
                    </td>
                  )}
                  {groupedColumns.map((groupInfo, groupIndex) => {
                    const isFirstGroup = groupIndex === 0;
                    const isLastGroup = groupIndex === groupedColumns.length - 1;

                    return groupInfo.columns.map((column, colIndex) => {
                      const isFirstColumn = colIndex === 0;
                      const value = row[column.key];
                      const isLinkColumn = linkColumns.includes(column.key);
                      const cellColor = getValueColor(value as number, column.type);
                      const isSticky = stickyColumns.includes(column.key);
                      const leftPosition = stickyPositionMap.get(column.key);

                      return (
                        <td
                          key={String(column.key)}
                          className={`table-cell ${column.width} ${
                            column.render ? '' : 'whitespace-nowrap'
                          } ${
                            column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                          } ${cellColor} border-b border-gray-100 dark:border-gray-800 px-2 py-2 text-xs ${isFirstGroup && isFirstColumn ? 'border-l-2' : ''} ${isLastGroup && colIndex === groupInfo.columns.length - 1 ? 'border-r-2' : ''} ${isFirstColumn ? 'border-l' : ''} ${isSticky ? 'sticky z-20 bg-white dark:bg-gray-900 border-r border-gray-100 dark:border-gray-800' : ''}`}
                          style={isSticky && leftPosition !== undefined ? { left: `${leftPosition}px` } : {}}
                        >
                          {isLinkColumn ? (
                            <a
                              href={getEastMoneyUrl(String(column.key === 'code' ? value : (row as { code: string }).code))}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary hover:text-primary/80 flex items-center gap-1 transition-colors duration-200 hover:underline whitespace-nowrap"
                            >
                              <span className="font-medium">{formatCellValue(value, column)}</span>
                              {column.key === 'code' && <ExternalLink size={10} className="opacity-60" />}
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
                    });
                  })}
                </tr>
                {expandedRow && selectedCodes.has(rowKey(row)) && (
                  <tr key={`${rowKey(row)}-expanded`}>
                    <td colSpan={columns.length + (selectable ? 1 : 0)} className="px-4 py-2 bg-gray-50 dark:bg-gray-800">
                      {expandedRow}
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
