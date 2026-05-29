import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Button } from '../components/common';
import { TrendingUp, Download, X } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';
import { TablePagination } from '../components/common/TablePagination';
import type { ColumnConfig } from '../utils/format';
import { getTodayIso } from '../utils/format';

interface LimitUpStock {
  code: string;
  name: string;
  reason: string;
  detail_reason: string;
  turnover_rate: number | null;
  volume: number | null;
  amount: number | null;
  change_pct: number | null;
  price: number | null;
  ups_downs: number | null;
  dde: number | null;
}

interface LimitUpResponse {
  date: string;
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  data: LimitUpStock[];
  message?: string;
  is_trading_day?: boolean;
}

type SortField = keyof LimitUpStock;
type SortOrder = 'asc' | 'desc';

const COLUMN_CONFIG: ColumnConfig<LimitUpStock>[] = [
  { key: 'code', label: '代码', width: 'w-20', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-24', align: 'left', type: 'text' },
  { key: 'reason', label: '涨停原因', width: 'w-40', align: 'left', type: 'text' },
  { key: 'detail_reason', label: '详细原因', width: 'w-80', align: 'left', type: 'text' },
  { key: 'price', label: '最新价', width: 'w-24', align: 'right', type: 'price' },
  { key: 'change_pct', label: '涨跌幅', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'turnover_rate', label: '换手率', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'volume', label: '成交量', width: 'w-28', align: 'right', type: 'number' },
  { key: 'amount', label: '成交额', width: 'w-28', align: 'right', type: 'money' },
  { key: 'dde', label: 'DDE净额', width: 'w-28', align: 'right', type: 'money' },
];

const LimitUpPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  useEffect(() => {
    document.title = '涨停揭秘 - STOCK';
  }, []);

  const urlDate = searchParams.get('date');
  const [selectedDate, setSelectedDate] = useState(urlDate || getTodayIso());

  useEffect(() => {
    const urlDate = searchParams.get('date');
    if (urlDate && urlDate !== selectedDate) {
      setSelectedDate(urlDate);
    }
  }, [searchParams]);
  
  const [stockList, setStockList] = useState<LimitUpStock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  const [sortField, setSortField] = useState<SortField>('change_pct');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  
  const [expandedStock, setExpandedStock] = useState<string | null>(null);
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(searchKeyword);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchKeyword]);

  const fetchLimitUpData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        date: selectedDate,
        page: String(currentPage),
        page_size: String(pageSize),
        sort_field: sortField,
        sort_order: sortOrder,
      });
      
      if (debouncedKeyword.trim()) {
        params.append('keyword', debouncedKeyword.trim());
      }
      
      const url = `/api/v1/limitup/?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('获取数据失败');
      }

      const result: LimitUpResponse = await response.json();

      if (result.data && Array.isArray(result.data)) {
        setStockList(result.data);
        setTotalCount(result.count);
        setTotalPages(result.total_pages || 0);
        setNoticeMessage(result.message || null);
      } else {
        setStockList([]);
        setTotalCount(0);
        setTotalPages(0);
        setNoticeMessage(result.message || null);
      }
    } catch (err) {
      console.error('获取涨停数据失败:', err);
      setError('获取涨停数据失败，请稍后重试');
      setStockList([]);
      setTotalCount(0);
      setTotalPages(0);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    setSelectedCodes(new Set());
    void fetchLimitUpData();
  }, [selectedDate, pageSize, debouncedKeyword]);

  useEffect(() => {
    setSelectedCodes(new Set());
    void fetchLimitUpData();
  }, [currentPage, sortField, sortOrder]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  const handleColumnSort = (field: string) => {
    const sortKey = field as SortField;
    if (sortField === sortKey) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(sortKey);
      setSortOrder('desc');
    }
  };

  const handleSelectAll = () => {
    if (selectedCodes.size === stockList.length) {
      setSelectedCodes(new Set());
    } else {
      setSelectedCodes(new Set(stockList.map(s => s.code)));
    }
  };

  const handleSelectRow = (code: string) => {
    const newSelected = new Set(selectedCodes);
    if (newSelected.has(code)) {
      newSelected.delete(code);
    } else {
      newSelected.add(code);
    }
    setSelectedCodes(newSelected);
  };

  const handleExport = () => {
    const exportList = selectedCodes.size > 0 
      ? stockList.filter(s => selectedCodes.has(s.code))
      : stockList;
    
    const headers = COLUMN_CONFIG.map(col => col.label).join(',');
    const rows = exportList.map(stock => {
      return COLUMN_CONFIG.map(col => {
        const value = (stock as any)[col.key];
        if (value === null || value === undefined) return '';
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return String(value);
      }).join(',');
    });
    
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `limitup_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const customColumns = COLUMN_CONFIG.map(col => {
    if (col.key === 'detail_reason') {
      return {
        ...col,
        render: (value: string, stock: LimitUpStock) => (
          <div
            className={`cursor-pointer select-none transition-all duration-200 ${
              expandedStock === stock.code ? 'whitespace-pre-wrap' : 'line-clamp-1'
            }`}
            title={value}
            onDoubleClick={() => setExpandedStock(expandedStock === stock.code ? null : stock.code)}
          >
            <span className="text-gray-700 dark:text-gray-300">{value || '-'}</span>
            {expandedStock === stock.code && (
              <span className="ml-2 text-xs text-gray-400">(双击收起)</span>
            )}
          </div>
        )
      };
    }
    if (col.key === 'reason') {
      return {
        ...col,
        render: (value: string) => (
          <span className="truncate max-w-xs" title={value}>
            {value || '-'}
          </span>
        )
      };
    }
    return col;
  });

  return (
    <div className="min-h-screen space-y-6 p-4 md:p-6 bg-gradient-to-br from-gray-50/50 to-blue-50/30 dark:from-gray-900 dark:to-gray-800">
      {/* Header Section */}
      <section className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="page-title-icon bg-gradient-to-br from-red-500/10 to-orange-500/10">
            <TrendingUp className="w-8 h-8 text-red-500" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              涨停揭秘
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
              每日涨停股票分析，包含涨停原因、换手率、成交量等信息
            </p>
          </div>
        </div>

        {/* Filter Card */}
        <Card className="filter-card">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              {/* Date Picker */}
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">日期:</span>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setSearchParams({ date: e.target.value });
                  }}
                  className="input-enhanced w-40"
                  max={getTodayIso()}
                />
              </div>

              {/* Search Input */}
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">搜索:</span>
                <div className="relative">
                  <input
                    type="text"
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                    placeholder="代码/名称/原因..."
                    className="input-enhanced pl-3 pr-8 w-56"
                  />
                  {searchKeyword && (
                    <button
                      type="button"
                      onClick={() => setSearchKeyword('')}
                      className="absolute right-2 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    >
                      <X className="w-3.5 h-3.5 text-gray-400" />
                    </button>
                  )}
                </div>
              </div>

              {/* Export Button */}
              <Button
                variant="secondary"
                onClick={handleExport}
                className="btn-with-icon"
              >
                <Download size={16} />
                {selectedCodes.size > 0 ? `导出选中(${selectedCodes.size})` : '导出'}
              </Button>
            </div>

            {/* Stats Badge */}
            <div className="stat-badge bg-gradient-to-r from-red-500 to-orange-500 text-white">
              <TrendingUp size={16} className="mr-1" />
              {totalCount} 只涨停
            </div>
          </div>
        </Card>

        {/* Notice Message */}
        {noticeMessage && (
          <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 border-blue-200 dark:border-blue-700">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-sm text-blue-800 dark:text-blue-200">{noticeMessage}</span>
            </div>
          </Card>
        )}
      </section>

      {/* Error State */}
      {error ? (
        <Card>
          <div className="text-center py-16">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-red-600 dark:text-red-400 text-lg font-medium mb-4">{error}</p>
            <Button
              variant="primary"
              onClick={() => {
                setCurrentPage(1);
                void fetchLimitUpData();
              }}
            >
              重新加载
            </Button>
          </div>
        </Card>
      ) : (
        <>
          {/* Data Table */}
          <Card>
            <DataTable
              columns={customColumns}
              data={stockList}
              loading={isLoading}
              emptyText="暂无数据"
              emptyDescription={noticeMessage || '没有找到符合条件的涨停股票数据'}
              selectable
              selectedCodes={selectedCodes}
              onSelectAll={handleSelectAll}
              onSelectRow={handleSelectRow}
              sortField={String(sortField)}
              sortOrder={sortOrder}
              onSort={handleColumnSort}
              linkColumns={['code', 'name']}
              rowKey={(row) => row.code}
              stickyColumns={['code', 'name']}
            />
          </Card>

          {/* Pagination */}
          {stockList.length > 0 && totalPages > 1 && (
            <TablePagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalCount={totalCount}
              pageSize={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
            />
          )}
        </>
      )}
    </div>
  );
};

export default LimitUpPage;
