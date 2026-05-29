import { useState, useEffect, useCallback } from 'react';

export type SortOrder = 'asc' | 'desc';

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
}

export interface SortState<T> {
  sortField: T;
  sortOrder: SortOrder;
}

export interface SelectionState {
  selectedCodes: Set<string>;
  isAllSelected: boolean;
}

export function useTableState<T>(initialPageSize = 20) {
  const [pagination, setPagination] = useState<PaginationState>({
    currentPage: 1,
    pageSize: initialPageSize,
    totalCount: 0,
    totalPages: 0,
  });

  const [sort, setSort] = useState<SortState<T>>({
    sortField: '' as T,
    sortOrder: 'desc',
  });

  const [selection, setSelection] = useState<SelectionState>({
    selectedCodes: new Set(),
    isAllSelected: false,
  });

  const [keyword, setKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(keyword);
    }, 500);
    return () => clearTimeout(timer);
  }, [keyword]);

  const handlePageChange = useCallback((page: number) => {
    if (page >= 1 && page <= pagination.totalPages) {
      setPagination(prev => ({ ...prev, currentPage: page }));
    }
  }, [pagination.totalPages]);

  const handlePageSizeChange = useCallback((size: number) => {
    setPagination(prev => ({ ...prev, pageSize: size, currentPage: 1 }));
  }, []);

  const handleSortChange = useCallback((field: T, order?: SortOrder) => {
    setSort(prev => ({
      sortField: field,
      sortOrder: order || (prev.sortField === field && prev.sortOrder === 'asc' ? 'desc' : 'asc'),
    }));
  }, []);

  const handleSelectAll = useCallback((data: T[], getCode: (item: T) => string) => {
    setSelection(prev => {
      if (prev.isAllSelected) {
        return { selectedCodes: new Set(), isAllSelected: false };
      } else {
        return { selectedCodes: new Set(data.map(getCode)), isAllSelected: true };
      }
    });
  }, []);

  const handleSelectRow = useCallback((code: string) => {
    setSelection(prev => {
      const newSelected = new Set(prev.selectedCodes);
      if (newSelected.has(code)) {
        newSelected.delete(code);
      } else {
        newSelected.add(code);
      }
      return { selectedCodes: newSelected, isAllSelected: false };
    });
  }, []);

  const clearSelection = useCallback(() => {
    setSelection({ selectedCodes: new Set(), isAllSelected: false });
  }, []);

  const resetPagination = useCallback(() => {
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  }, []);

  const updatePagination = useCallback((count: number, totalPages: number) => {
    setPagination(prev => ({ ...prev, totalCount: count, totalPages }));
  }, []);

  return {
    pagination,
    sort,
    selection,
    keyword,
    debouncedKeyword,
    setKeyword,
    setSort,
    handlePageChange,
    handlePageSizeChange,
    handleSortChange,
    handleSelectAll,
    handleSelectRow,
    clearSelection,
    resetPagination,
    updatePagination,
  };
}
