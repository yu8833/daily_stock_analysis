import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Badge, Button } from '../components/common';
import { TrendingDown, Download, X } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';
import { TablePagination } from '../components/common/TablePagination';
import type { ColumnConfig } from '../utils/format';
import { getTodayIso } from '../utils/format';

interface SellStock {
  code: string;
  name: string;
  reason: string;
  signal_count: number;
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
  short_avg_array: string | null;
  high_funds_outflow: string | null;
  upper_large_volume: string | null;
  shooting_star: string | null;
  evening_star: string | null;
  black_cloud_tops: string | null;
  bearish_engulfing: string | null;
  down_7days: string | null;
  breakdown_ma_5days: string | null;
  breakdown_ma_10days: string | null;
  breakdown_ma_20days: string | null;
  breakdown_ma_60days: string | null;
  macd_dead_fork: string | null;
  macd_dead_forkz: string | null;
  macd_dead_forky: string | null;
  kdj_dead_fork: string | null;
  kdj_dead_forkz: string | null;
  kdj_dead_forky: string | null;
  down_narrow_volume: string | null;
  climax_limitdown: string | null;
  now_newlow: string | null;
  low_recent_3days: string | null;
  low_recent_5days: string | null;
  low_recent_10days: string | null;
  low_recent_20days: string | null;
  low_recent_30days: string | null;
  lose_market_3days: string | null;
  lose_market_5days: string | null;
  lose_market_10days: string | null;
  lose_market_20days: string | null;
  lose_market_30days: string | null;
}

type SortField = keyof SellStock;
type SortOrder = 'asc' | 'desc';

const COLUMN_GROUPS = [
  { id: 'basic', label: '基本信息' },
  { id: 'kline', label: 'K线形态' },
  { id: 'technical', label: '技术指标' },
  { id: 'performance', label: '近期表现' },
  { id: 'strategy', label: '策略信号' },
  { id: 'fund_flow', label: '资金流向' },
  { id: 'quotation', label: '行情数据' },
];

const COLUMN_CONFIG: ColumnConfig<SellStock>[] = [
  { key: 'code', label: '代码', width: 'w-16', align: 'left', type: 'text', group: 'basic' },
  { key: 'name', label: '名称', width: 'w-16', align: 'left', type: 'text', group: 'basic' },
  { key: 'reason', label: '卖出理由', width: 'w-40', align: 'left', type: 'text', group: 'basic' },
  { key: 'signal_count', label: '信号数', width: 'w-16', align: 'center', type: 'number', group: 'basic' },

  { key: 'down_7days', label: '七连阴', width: 'w-16', align: 'center', type: 'flag', group: 'kline' },
  { key: 'shooting_star', label: '射击之星', width: 'w-18', align: 'center', type: 'flag', group: 'kline' },
  { key: 'evening_star', label: '黄昏之星', width: 'w-18', align: 'center', type: 'flag', group: 'kline' },
  { key: 'black_cloud_tops', label: '乌云盖顶', width: 'w-18', align: 'center', type: 'flag', group: 'kline' },
  { key: 'bearish_engulfing', label: '穿头破脚', width: 'w-18', align: 'center', type: 'flag', group: 'kline' },

  { key: 'macd_dead_fork', label: 'MACD死叉', width: 'w-18', align: 'center', type: 'flag', group: 'technical' },
  { key: 'macd_dead_forkz', label: 'MACD周死叉', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'macd_dead_forky', label: 'MACD月死叉', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'kdj_dead_fork', label: 'KDJ死叉', width: 'w-18', align: 'center', type: 'flag', group: 'technical' },
  { key: 'kdj_dead_forkz', label: 'KDJ周死叉', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'kdj_dead_forky', label: 'KDJ月死叉', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'breakdown_ma_5days', label: '破5日线', width: 'w-18', align: 'center', type: 'flag', group: 'technical' },
  { key: 'breakdown_ma_10days', label: '破10日线', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'breakdown_ma_20days', label: '破20日线', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'breakdown_ma_60days', label: '破60日线', width: 'w-20', align: 'center', type: 'flag', group: 'technical' },
  { key: 'short_avg_array', label: '均线空头', width: 'w-18', align: 'center', type: 'flag', group: 'technical' },

  { key: 'lose_market_3days', label: '跑输大盘3日', width: 'w-20', align: 'center', type: 'flag', group: 'performance' },
  { key: 'lose_market_5days', label: '跑输大盘5日', width: 'w-20', align: 'center', type: 'flag', group: 'performance' },
  { key: 'lose_market_10days', label: '跑输大盘10日', width: 'w-22', align: 'center', type: 'flag', group: 'performance' },
  { key: 'now_newlow', label: '今日历史新低', width: 'w-20', align: 'center', type: 'flag', group: 'performance' },
  { key: 'low_recent_3days', label: '历史新低3日', width: 'w-20', align: 'center', type: 'flag', group: 'performance' },
  { key: 'low_recent_5days', label: '历史新低5日', width: 'w-20', align: 'center', type: 'flag', group: 'performance' },
  { key: 'low_recent_10days', label: '历史新低10日', width: 'w-22', align: 'center', type: 'flag', group: 'performance' },

  { key: 'upper_large_volume', label: '连涨放量', width: 'w-18', align: 'center', type: 'flag', group: 'strategy' },
  { key: 'down_narrow_volume', label: '下跌无量', width: 'w-18', align: 'center', type: 'flag', group: 'strategy' },
  { key: 'climax_limitdown', label: '放量跌停', width: 'w-18', align: 'center', type: 'flag', group: 'strategy' },

  { key: 'high_funds_outflow', label: '高位资金净流出', width: 'w-24', align: 'center', type: 'flag', group: 'fund_flow' },

  { key: 'industry', label: '行业', width: 'w-28', align: 'left', type: 'text', group: 'quotation' },
  { key: 'area', label: '地区', width: 'w-20', align: 'left', type: 'text', group: 'quotation' },
  { key: 'new_price', label: '最新价', width: 'w-24', align: 'right', type: 'price', group: 'quotation' },
  { key: 'change_rate', label: '涨跌幅', width: 'w-24', align: 'right', type: 'percent', group: 'quotation' },
  { key: 'volume_ratio', label: '量比', width: 'w-20', align: 'right', type: 'number', group: 'quotation' },
  { key: 'volume', label: '成交量', width: 'w-28', align: 'right', type: 'number', group: 'quotation' },
  { key: 'deal_amount', label: '成交额', width: 'w-28', align: 'right', type: 'money', group: 'quotation' },
  { key: 'turnoverrate', label: '换手率', width: 'w-24', align: 'right', type: 'percent', group: 'quotation' },
  { key: 'pe', label: 'PE', width: 'w-16', align: 'right', type: 'number', group: 'quotation' },
  { key: 'pbnewmrq', label: 'PB', width: 'w-16', align: 'right', type: 'number', group: 'quotation' },
  { key: 'total_market_cap', label: '总市值', width: 'w-28', align: 'right', type: 'money', group: 'quotation' },
];

const SellPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  
  useEffect(() => {
    document.title = '卖出信号 - STOCK';
  }, []);

  const urlDate = searchParams.get('date');
  const [selectedDate, setSelectedDate] = useState(urlDate || getTodayIso());

  useEffect(() => {
    const urlDate = searchParams.get('date');
    if (urlDate && urlDate !== selectedDate) {
      setSelectedDate(urlDate);
    }
  }, [searchParams]);
  
  const [stockList, setStockList] = useState<SellStock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  const [sortField, setSortField] = useState<SortField>('change_rate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');
  
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set());
  const [flagFilters, setFlagFilters] = useState<Record<string, string>>({});

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedKeyword(searchKeyword);
    }, 500);
    return () => clearTimeout(timer);
  }, [searchKeyword]);

  const handleFlagFilterChange = (key: string, value: string) => {
    setFlagFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setCurrentPage(1);
    setSelectedCodes(new Set());
  };

  const fetchSellData = async () => {
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
      
      for (const [key, value] of Object.entries(flagFilters)) {
        if (value) {
          params.append(key, value);
        }
      }
      
      const url = `/api/v1/sell/?${params.toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      setStockList(result.data || []);
      setTotalCount(result.count || 0);
      setTotalPages(result.total_pages || 0);
      setNoticeMessage(result.message || null);
    } catch (err) {
      console.error('获取卖出信号数据失败:', err);
      setError('获取卖出信号数据失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    setSelectedCodes(new Set());
    void fetchSellData();
  }, [selectedDate, pageSize, debouncedKeyword]);

  useEffect(() => {
    setSelectedCodes(new Set());
    void fetchSellData();
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
    link.setAttribute('download', `sell_signal_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const customColumns = COLUMN_CONFIG.map(col => {
    if (col.type === 'flag') {
      return {
        ...col,
        render: (value: any) => {
          if (value === 'Y' || value === '1' || value === 1 || value === '是') {
            return <Badge variant="danger">是</Badge>;
          } else if (value === 'N' || value === '0' || value === 0 || value === '否') {
            return <Badge variant="default">否</Badge>;
          } else {
            return '-';
          }
        }
      };
    }
    return col;
  });

  return (
    <div className="min-h-screen space-y-6 p-4 md:p-6 bg-gradient-to-br from-gray-50/50 to-red-50/30 dark:from-gray-900 dark:to-gray-800">
      <section className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="page-title-icon bg-gradient-to-br from-red-500/10 to-rose-500/10">
            <TrendingDown className="w-8 h-8 text-red-500" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              卖出信号
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
              根据技术指标筛选出具有卖出信号的股票（均线空头排列、高位资金净流出、K线形态等）
            </p>
          </div>
        </div>

        <Card className="filter-card">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
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

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">搜索:</span>
                <div className="relative">
                  <input
                    type="text"
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                    placeholder="代码/名称/行业(支持正则)..."
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

              <Button
                variant="secondary"
                onClick={handleExport}
                className="btn-with-icon"
              >
                <Download size={16} />
                {selectedCodes.size > 0 ? `导出选中(${selectedCodes.size})` : '导出CSV'}
              </Button>
            </div>

            <div className="stat-badge bg-gradient-to-r from-red-500 to-rose-500 text-white">
              <TrendingDown size={16} className="mr-1" />
              {totalCount} 只股票
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

      {error ? (
        <Card>
          <div className="text-center py-16">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-red-600 dark:text-red-400 text-lg font-medium mb-4">{error}</p>
            <Button
              variant="primary"
              onClick={() => {
                setCurrentPage(1);
                void fetchSellData();
              }}
            >
              重新加载
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <Card>
            <DataTable
              columns={customColumns}
              data={stockList}
              loading={isLoading}
              emptyText="暂无数据"
              emptyDescription="没有找到符合条件的卖出信号股票"
              selectable
              selectedCodes={selectedCodes}
              onSelectAll={handleSelectAll}
              onSelectRow={handleSelectRow}
              sortField={String(sortField)}
              sortOrder={sortOrder}
              onSort={handleColumnSort}
              linkColumns={['code', 'name']}
              rowKey={(row) => row.code}
              groups={COLUMN_GROUPS}
              flagFilters={flagFilters}
              onFlagFilterChange={handleFlagFilterChange}
            />
          </Card>

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

export default SellPage;