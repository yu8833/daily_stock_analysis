import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Badge, EmptyState, Loading, Checkbox } from '../components/common';
import { TrendingUp, ExternalLink, ArrowUp, ArrowDown, Download } from 'lucide-react';

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

const COLUMN_CONFIG: { key: SortField; label: string; width: string; align: 'left' | 'right' | 'center'; type: 'text' | 'number' | 'percent' | 'money' | 'price' }[] = [
  { key: 'code', label: '代码', width: 'w-16', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-20', align: 'left', type: 'text' },
  { key: 'reason', label: '涨停原因', width: 'w-32', align: 'left', type: 'text' },
  { key: 'detail_reason', label: '详细原因', width: 'w-64', align: 'left', type: 'text' },
  { key: 'price', label: '最新价', width: 'w-20', align: 'right', type: 'price' },
  { key: 'change_pct', label: '涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'turnover_rate', label: '换手率', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'volume', label: '成交量', width: 'w-24', align: 'right', type: 'number' },
  { key: 'amount', label: '成交额', width: 'w-24', align: 'right', type: 'money' },
  { key: 'dde', label: 'DDE净额', width: 'w-24', align: 'right', type: 'money' },
];

function getTodayIso(): string {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

const formatPct = (value: number | null | undefined): string => {
  if (value == null) return '-';
  const formatted = value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
  return formatted;
};

const formatNumber = (value: number | null | undefined): string => {
  if (value == null) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(0);
};

const formatMoney = (value: number | null | undefined): string => {
  if (value == null) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(2);
};

const formatPrice = (value: number | null | undefined): string => {
  if (value == null) return '-';
  return value.toFixed(2);
};

const getEastMoneyUrl = (code: string): string => {
  if (code.startsWith('6') || code.startsWith('5') || code.startsWith('9')) {
    return `https://quote.eastmoney.com/sh${code}.html`;
  } else {
    return `https://quote.eastmoney.com/sz${code}.html`;
  }
};

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

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const handleColumnSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
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

  const renderCellValue = (stock: LimitUpStock, column: typeof COLUMN_CONFIG[0]) => {
    const value = (stock as any)[column.key];
    if (value === null || value === undefined) return '-';

    switch (column.type) {
      case 'price':
        return formatPrice(value);
      case 'percent':
        return formatPct(value);
      case 'money':
        return formatMoney(value);
      case 'number':
        return formatNumber(value);
      default:
        return String(value);
    }
  };

  const getValueColor = (value: number | null | undefined, type: string) => {
    if (type === 'percent' && value !== null && value !== undefined) {
      if (value > 0) return 'text-red-600 dark:text-red-400';
      if (value < 0) return 'text-green-600 dark:text-green-400';
    }
    if (type === 'money' && value !== null && value !== undefined) {
      if (value > 0) return 'text-red-600 dark:text-red-400';
      if (value < 0) return 'text-green-600 dark:text-green-400';
    }
    return '';
  };

  return (
    <div className="limitup-page min-h-screen space-y-4 p-4 md:p-6">
      <section className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-success/10">
            <TrendingUp className="w-6 h-6 text-success" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-semibold text-foreground">涨停揭秘</h1>
            <p className="text-xs md:text-sm text-secondary">
              每日涨停股票分析，包含涨停原因、换手率、成交量等信息
            </p>
          </div>
        </div>

        <Card padding="md">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <label className="text-sm text-secondary">选择日期</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => {
                  setSelectedDate(e.target.value);
                  setSearchParams({ date: e.target.value });
                }}
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none"
                max={getTodayIso()}
              />
              <label className="text-sm text-secondary">关键字</label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="代码/名称/原因..."
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none w-48"
              />
              {searchKeyword && (
                <button
                  type="button"
                  onClick={() => setSearchKeyword('')}
                  className="text-xs text-secondary hover:text-primary"
                >
                  清除
                </button>
              )}
              <button
                type="button"
                onClick={handleExport}
                className="btn-secondary h-10 px-3 flex items-center gap-2"
              >
                <Download size={14} />
                {selectedCodes.size > 0 ? `导出选中(${selectedCodes.size})` : '导出'}
              </button>
            </div>
            <Badge variant="success">{totalCount} 只涨停</Badge>
          </div>
        </Card>

        {noticeMessage && (
          <Card padding="md">
            <div className="flex items-center gap-2 text-secondary">
              <span className="text-sm">{noticeMessage}</span>
            </div>
          </Card>
        )}
      </section>

      {error ? (
        <Card padding="md">
          <div className="text-center py-8">
            <p className="text-danger">{error}</p>
            <button
              onClick={() => {
                setCurrentPage(1);
                void fetchLimitUpData();
              }}
              className="btn-primary mt-4"
            >
              重新加载
            </button>
          </div>
        </Card>
      ) : (
        <Card>
          {isLoading ? (
            <div className="flex items-center justify-center min-h-[400px] py-12">
              <Loading label="获取股票数据中..." />
            </div>
          ) : (
            <div className="relative">
              <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="w-12 px-3 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        <Checkbox
                          checked={stockList.length > 0 && selectedCodes.size === stockList.length}
                          onChange={handleSelectAll}
                        />
                      </th>
                      {COLUMN_CONFIG.map(column => (
                        <th
                          key={column.key}
                          className={`px-3 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${column.width} ${
                            column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                          }`}
                        >
                          <button
                            type="button"
                            onClick={() => handleColumnSort(column.key)}
                            className="flex items-center justify-center gap-1 cursor-pointer"
                          >
                            <span>{column.label}</span>
                            {sortField === column.key && (
                              sortOrder === 'asc' ? (
                                <ArrowUp size={14} className="text-blue-500" />
                              ) : (
                                <ArrowDown size={14} className="text-blue-500" />
                              )
                            )}
                          </button>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {stockList.length === 0 ? (
                      <tr>
                        <td colSpan={COLUMN_CONFIG.length + 1} className="px-6 py-12 text-center">
                          <EmptyState
                            title="暂无数据"
                            description={noticeMessage || '没有找到符合条件的涨停股票数据'}
                          />
                        </td>
                      </tr>
                    ) : (
                      stockList.map(stock => (
                        <React.Fragment key={stock.code}>
                          <tr className="hover:bg-gray-50 dark:hover:bg-gray-800">
                            <td className="px-3 py-3">
                              <Checkbox
                                checked={selectedCodes.has(stock.code)}
                                onChange={() => handleSelectRow(stock.code)}
                              />
                            </td>
                            {COLUMN_CONFIG.map(column => (
                              <td
                                key={column.key}
                                className={`px-3 py-3 text-sm text-gray-900 dark:text-gray-100 ${column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'} ${getValueColor((stock as any)[column.key], column.type)} ${column.key !== 'detail_reason' ? 'whitespace-nowrap' : ''}`}
                              >
                                {column.key === 'code' || column.key === 'name' ? (
                                  <a
                                    href={getEastMoneyUrl(stock.code)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center gap-1"
                                  >
                                    {renderCellValue(stock, column)}
                                    {column.key === 'code' && <ExternalLink size={12} />}
                                  </a>
                                ) : column.key === 'detail_reason' ? (
                                  <span 
                                    className={`cursor-pointer ${expandedStock === stock.code ? 'whitespace-pre-wrap' : 'line-clamp-1'}`}
                                    title={stock.detail_reason}
                                    onDoubleClick={() => setExpandedStock(expandedStock === stock.code ? null : stock.code)}
                                  >
                                    {stock.detail_reason}
                                  </span>
                                ) : (
                                  <span className="truncate max-w-[200px]" title={column.key === 'reason' ? stock.reason : undefined}>
                                    {renderCellValue(stock, column)}
                                  </span>
                                )}
                              </td>
                            ))}
                          </tr>
                        </React.Fragment>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </Card>
      )}

      {stockList.length > 0 && totalPages > 1 && (
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center gap-4">
            <span className="text-sm text-secondary">
              共 {totalCount} 条记录
            </span>
            <div className="flex items-center gap-2">
              <span className="text-sm text-secondary">每页显示:</span>
              <select
                value={pageSize}
                onChange={handlePageSizeChange}
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
          
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="btn-secondary h-8 px-3 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              上一页
            </button>
            
            {(() => {
              const visiblePages = 5;
              let start = 1;
              
              if (totalPages > visiblePages) {
                if (currentPage <= 3) {
                  start = 1;
                } else if (currentPage >= totalPages - 2) {
                  start = totalPages - 4;
                } else {
                  start = currentPage - 2;
                }
              }
              
              const pageNumbers = [];
              for (let i = 0; i < visiblePages && start + i <= totalPages; i++) {
                pageNumbers.push(start + i);
              }
              
              return pageNumbers.map((pageNum) => (
                <button
                  key={pageNum}
                  type="button"
                  onClick={() => handlePageChange(pageNum)}
                  className={`h-8 w-8 px-2 rounded ${
                    currentPage === pageNum
                      ? 'bg-primary text-white'
                      : 'btn-secondary'
                  }`}
                >
                  {pageNum}
                </button>
              ));
            })()}
            
            <button
              type="button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="btn-secondary h-8 px-3 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              下一页
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LimitUpPage;
