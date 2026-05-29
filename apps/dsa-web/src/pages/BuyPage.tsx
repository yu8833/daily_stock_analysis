import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Badge, EmptyState, Loading, Checkbox } from '../components/common';
import { Search, ExternalLink, ArrowUp, ArrowDown, Download } from 'lucide-react';

interface BuyStock {
  code: string;
  name: string;
  new_price: number | null;
  change_rate: number | null;
  volume_ratio: number | null;
  high_price: number | null;
  low_price: number | null;
  pre_close_price: number | null;
  volume: number | null;
  deal_amount: number | null;
  turnoverrate: number | null;
  listing_date: string | null;
  industry: string | null;
  area: string | null;
  concept: string | null;
  pe: number | null;
  pbnewmrq: number | null;
  total_market_cap: number | null;
  free_cap: number | null;
  ma5: number | null;
  ma10: number | null;
  ma20: number | null;
  ma60: number | null;
  ma120: number | null;
  ma250: number | null;
  macd_golden_fork: string | null;
  kdj_golden_fork: string | null;
  break_through: string | null;
  long_avg_array: string | null;
  short_avg_array: string | null;
  low_funds_inflow: string | null;
  high_funds_outflow: string | null;
}

type SortField = keyof BuyStock;
type SortOrder = 'asc' | 'desc';

const COLUMN_CONFIG: { key: SortField; label: string; width: string; align: 'left' | 'right' | 'center'; type: 'text' | 'number' | 'percent' | 'money' | 'price' | 'date' | 'flag' }[] = [
  { key: 'code', label: '代码', width: 'w-16', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-20', align: 'left', type: 'text' },
  { key: 'macd_golden_fork', label: 'MACD金叉', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'kdj_golden_fork', label: 'KDJ金叉', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'break_through', label: '放量突破', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'long_avg_array', label: '均线多头', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'low_funds_inflow', label: '低位资金净流入', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'industry', label: '行业', width: 'w-24', align: 'left', type: 'text' },
  { key: 'area', label: '地区', width: 'w-16', align: 'left', type: 'text' },
  { key: 'new_price', label: '最新价', width: 'w-20', align: 'right', type: 'price' },
  { key: 'change_rate', label: '涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'volume_ratio', label: '量比', width: 'w-16', align: 'right', type: 'number' },
  { key: 'volume', label: '成交量', width: 'w-24', align: 'right', type: 'number' },
  { key: 'deal_amount', label: '成交额', width: 'w-24', align: 'right', type: 'money' },
  { key: 'turnoverrate', label: '换手率', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'pe', label: 'PE', width: 'w-14', align: 'right', type: 'number' },
  { key: 'pbnewmrq', label: 'PB', width: 'w-14', align: 'right', type: 'number' },
  { key: 'total_market_cap', label: '总市值', width: 'w-24', align: 'right', type: 'money' },
];

const formatPct = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  const formatted = value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
  return formatted;
};

const formatNumber = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(0);
};

const formatMoney = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(2);
};

const formatPrice = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  return value.toFixed(2);
};

const getEastMoneyUrl = (code: string): string => {
  if (code.startsWith('6') || code.startsWith('5') || code.startsWith('9')) {
    return `https://quote.eastmoney.com/sh${code}.html`;
  } else {
    return `https://quote.eastmoney.com/sz${code}.html`;
  }
};

const getTodayIso = (): string => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

const BuyPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  useEffect(() => {
    document.title = '买入信号 - STOCK';
  }, []);

  const urlDate = searchParams.get('date');
  const [selectedDate, setSelectedDate] = useState(urlDate || getTodayIso());

  useEffect(() => {
    const urlDate = searchParams.get('date');
    if (urlDate && urlDate !== selectedDate) {
      setSelectedDate(urlDate);
    }
  }, [searchParams]);
  const [stockList, setStockList] = useState<BuyStock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  const [sortField, setSortField] = useState<SortField>('change_rate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set());

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(searchKeyword);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchKeyword]);

  const fetchBuyData = async () => {
    setIsLoading(true);
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
      
      const url = `/api/v1/buy/?${params.toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setStockList(result.data || []);
      setTotalCount(result.count || 0);
      setTotalPages(result.total_pages || 0);
    } catch (err) {
      console.error('获取买入信号数据失败:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    void fetchBuyData();
  }, [selectedDate, pageSize, debouncedKeyword]);

  useEffect(() => {
    void fetchBuyData();
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
    link.setAttribute('download', `buy_signal_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderCellValue = (stock: BuyStock, column: typeof COLUMN_CONFIG[0]) => {
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
      case 'flag':
        if (value === 'Y' || value === '1' || value === 1 || value === '是') {
          return <Badge variant="success">是</Badge>;
        } else if (value === 'N' || value === '0' || value === 0 || value === '否') {
          return <Badge variant="default">否</Badge>;
        } else {
          return '-';
        }
      default:
        return String(value);
    }
  };

  const getValueColor = (value: number | null, type: string) => {
    if (type === 'percent' && value !== null) {
      if (value > 0) return 'text-red-600 dark:text-red-400';
      if (value < 0) return 'text-green-600 dark:text-green-400';
    }
    return '';
  };

  return (
    <div className="buy-page min-h-screen space-y-4 p-4 md:p-6">
      <section className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-success/10">
            <Search className="w-6 h-6 text-success" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-semibold text-foreground">买入信号</h1>
            <p className="text-xs md:text-sm text-secondary">
              根据技术指标筛选出具有买入信号的股票（MACD金叉、KDJ金叉、放量突破等）
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
                placeholder="代码/名称/行业..."
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
            <Badge variant="success">{totalCount} 只股票</Badge>
          </div>
        </Card>
      </section>

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
                          description="没有找到符合条件的买入信号股票"
                        />
                      </td>
                    </tr>
                  ) : (
                    stockList.map(stock => (
                      <tr key={stock.code} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-3 py-3">
                          <Checkbox
                            checked={selectedCodes.has(stock.code)}
                            onChange={() => handleSelectRow(stock.code)}
                          />
                        </td>
                        {COLUMN_CONFIG.map(column => (
                          <td
                            key={column.key}
                            className={`px-3 py-3 text-sm whitespace-nowrap text-gray-900 dark:text-gray-100 ${column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'} ${getValueColor((stock as any)[column.key], column.type)}`}
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
                            ) : (
                              renderCellValue(stock, column)
                            )}
                          </td>
                        ))}
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>

      {stockList.length > 0 && (
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

export default BuyPage;