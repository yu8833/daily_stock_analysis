import React from 'react';
import { Pagination } from './Pagination';
import { cn } from '../../utils/cn';

interface TablePaginationProps {
  currentPage: number;
  totalPages: number;
  totalCount: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  className?: string;
}

export const TablePagination: React.FC<TablePaginationProps> = ({
  currentPage,
  totalPages,
  totalCount,
  pageSize,
  onPageChange,
  onPageSizeChange,
  className = '',
}) => {
  if (totalCount === 0) return null;

  return (
    <div className={cn('flex flex-col sm:flex-row items-center justify-between gap-3 mt-4 pt-4 border-t border-white/10', className)}>
      <div className="flex items-center gap-4">
        <span className="text-sm text-secondary">
          共 {totalCount} 条记录
        </span>
        <div className="flex items-center gap-2">
          <span className="text-sm text-secondary">每页显示:</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="input-surface input-focus-glow h-8 rounded border bg-transparent px-2 text-sm"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
            <option value={100}>100</option>
          </select>
          <span className="text-sm text-secondary">条</span>
        </div>
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
      />
    </div>
  );
};
