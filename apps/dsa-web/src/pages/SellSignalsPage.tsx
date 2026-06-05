import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, Button } from '../components/common';
import { TrendingDown, RefreshCw, Search, Filter, Download, X } from 'lucide-react';
import { DataTable } from '../components/common/DataTable';
import type { ColumnConfig } from '../utils/format';
import { getTodayIso, getEastMoneyUrl } from '../utils/format';

interface SignalItem {
  code: string;
  name: string;
  stock_code: string;
  stock_name: string;
  signal_name: string;
  score: number;
  recommendation: string;
  signal_type: 'buy' | 'sell';
  date: string;
  new_price?: number;
  change_rate?: number;
  volume_ratio?: number;
  pe?: number;
  pbnewmrq?: number;
  roe_weight?: number;
  sale_gpr?: number;
  netprofit_yoy_ratio?: number;
}

const COLUMNS: ColumnConfig<SignalItem>[] = [
  { key: 'code', label: '代码', width: 'w-20', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-24', align: 'left', type: 'text' },
  { key: 'signal_name', label: '信号名称', width: 'w-32', align: 'left', type: 'text' },
  { key: 'score', label: '评分', width: 'w-20', align: 'right', type: 'number' },
  { key: 'new_price', label: '最新价', width: 'w-24', align: 'right', type: 'price' },
  { key: 'change_rate', label: '涨跌幅', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'volume_ratio', label: '量比', width: 'w-24', align: 'right', type: 'number' },
  { key: 'pe', label: '市盈率', width: 'w-24', align: 'right', type: 'number' },
  { key: 'pbnewmrq', label: '市净率', width: 'w-24', align: 'right', type: 'number' },
  { key: 'roe_weight', label: 'ROE', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'sale_gpr', label: '毛利率', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'netprofit_yoy_ratio', label: '净利增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'recommendation', label: '操作建议', width: 'w-48', align: 'left', type: 'text' },
];

const customColumns = COLUMNS.map((col) => {
  if (col.key === 'name') {
    return {
      ...col,
      render: (value: any, row: any) => {
        const code = row.code || row.stock_code;
        return (
          <a
            href={getEastMoneyUrl(String(code))}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:text-primary/80 flex items-center gap-1.5 transition-colors duration-200 hover:underline"
          >
            <span className="font-medium">{value}</span>
          </a>
        );
      },
    };
  }
  return col;
});

const SellSignalsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    document.title = '卖出信号 - STOCK';
  }, []);

  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const urlDate = searchParams.get('date');
    return urlDate || getTodayIso();
  });

  const [data, setData] = useState<SignalItem[]>([]);
  const [filteredData, setFilteredData] = useState<SignalItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [lastRefreshTime, setLastRefreshTime] = useState<string>('');
  const [selectedSignal, setSelectedSignal] = useState<string>('all');
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set());

  const signalOptions = [
    { value: 'all', label: '全部信号' },
    { value: 'S1', label: 'S1 - 加速卖点' },
    { value: 'S2', label: 'S2 - 跌破卖点' },
    { value: 'S3', label: 'S3 - 清仓卖点' },
  ];

  const fetchSellSignals = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/signals/sell?date=${selectedDate}`);
      if (!response.ok) {
        throw new Error('获取卖出信号失败');
      }
      const result: SignalItem[] = await response.json();
      setData(result);
      setFilteredData(result);

      const now = new Date();
      setLastRefreshTime(`${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`);
    } catch (err) {
      console.error('获取卖出信号失败:', err);
      setError('获取数据失败，请稍后重试');
      setData([]);
      setFilteredData([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const urlDate = searchParams.get('date');
    if (urlDate && urlDate !== selectedDate) {
      setSelectedDate(urlDate);
    }
  }, [searchParams, selectedDate]);

  useEffect(() => {
    void fetchSellSignals();
  }, [selectedDate]);

  useEffect(() => {
    let filtered = data;

    if (searchKeyword) {
      filtered = filtered.filter(item =>
        item.stock_code.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        item.stock_name.toLowerCase().includes(searchKeyword.toLowerCase())
      );
    }

    if (selectedSignal !== 'all') {
      filtered = filtered.filter(item => item.signal_name.includes(selectedSignal));
    }

    setFilteredData(filtered);
  }, [searchKeyword, selectedSignal, data]);

  const handleRefresh = () => {
    void fetchSellSignals();
  };

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
    setSearchParams({ date });
  };

  const handleSelectAll = () => {
    if (selectedCodes.size === filteredData.length) {
      setSelectedCodes(new Set());
    } else {
      setSelectedCodes(new Set(filteredData.map(s => s.code || s.stock_code)));
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
      ? filteredData.filter(s => selectedCodes.has(s.code || s.stock_code))
      : filteredData;

    const headers = COLUMNS.map(col => col.label).join(',');
    const rows = exportList.map(item => {
      return COLUMNS.map(col => {
        const value = (item as any)[col.key];
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
    link.setAttribute('download', `sell_signals_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen space-y-6 p-4 md:p-6 bg-gradient-to-br from-gray-50/50 to-red-50/30 dark:from-gray-900 dark:to-gray-800">
      <section className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="page-title-icon bg-gradient-to-br from-red-500/10 to-orange-500/10">
            <TrendingDown className="w-8 h-8 text-red-500" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              卖出信号
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
              当前日期: {selectedDate} | 基于均线三买三卖系统，自动扫描卖出信号
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
                  onChange={(e) => handleDateChange(e.target.value)}
                  className="input-enhanced w-40"
                  max={getTodayIso()}
                />
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <select
                  value={selectedSignal}
                  onChange={(e) => setSelectedSignal(e.target.value)}
                  className="input-enhanced w-40"
                >
                  {signalOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-gray-500" />
                <div className="relative">
                  <input
                    type="text"
                    value={searchKeyword}
                    onChange={(e) => setSearchKeyword(e.target.value)}
                    placeholder="代码/名称..."
                    className="input-enhanced pl-3 pr-8 w-48"
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

            <div className="flex items-center gap-4">
              <Button
                variant="secondary"
                onClick={handleRefresh}
                className="btn-with-icon"
                disabled={isLoading}
              >
                <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                {isLoading ? '刷新中...' : '刷新'}
              </Button>
              {lastRefreshTime && (
                <span className="text-xs text-gray-400">
                  最后刷新: {lastRefreshTime}
                </span>
              )}
              <div className="stat-badge bg-gradient-to-r from-red-500 to-orange-500 text-white">
                <TrendingDown size={16} className="mr-1" />
                {filteredData.length} 个信号
              </div>
            </div>
          </div>
        </Card>
      </section>

      {error ? (
        <Card>
          <div className="text-center py-16">
            <div className="text-4xl mb-4">⚠️</div>
            <p className="text-red-600 dark:text-red-400 text-lg font-medium mb-4">{error}</p>
            <Button variant="primary" onClick={handleRefresh}>
              重新加载
            </Button>
          </div>
        </Card>
      ) : (
        <Card padding="none">
          <DataTable
            columns={customColumns}
            data={filteredData}
            loading={isLoading}
            emptyText="暂无卖出信号"
            emptyDescription="当前没有符合条件的卖出信号"
            rowKey={(row) => `${row.code || row.stock_code}-${row.signal_name}`}
            selectable
            selectedCodes={selectedCodes}
            onSelectAll={handleSelectAll}
            onSelectRow={handleSelectRow}
          />
        </Card>
      )}
    </div>
  );
};

export default SellSignalsPage;