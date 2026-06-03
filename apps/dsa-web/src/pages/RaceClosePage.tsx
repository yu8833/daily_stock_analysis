import React, { useEffect, useState } from 'react';
import { TrendingDown, RefreshCw, Download, X, Search } from 'lucide-react';
import { Card, Button } from '../components/common';
import { DataTable } from '../components/common/DataTable';
import { TablePagination } from '../components/common/TablePagination';
import type { ColumnConfig } from '../utils/format';
import { getTodayIso } from '../utils/format';
import { marketDataApi } from '../api/marketData';
import type { ChipRaceItem } from '../api/marketData';

const COLUMNS: ColumnConfig<ChipRaceItem>[] = [
  { key: 'code', label: '代码', width: 'w-20', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-24', align: 'left', type: 'text' },
  { key: 'latest_price', label: '最新价', width: 'w-24', align: 'right', type: 'price' },
  { key: 'change_pct', label: '涨跌幅', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'race_amount', label: '抢筹金额', width: 'w-28', align: 'right', type: 'money' },
  { key: 'race_ratio', label: '抢筹占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'race_pct', label: '抢筹幅度', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'board_days', label: '连板天数', width: 'w-20', align: 'right', type: 'number' },
];

const RaceClosePage: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState(getTodayIso());
  const [searchKeyword, setSearchKeyword] = useState('');
  const [data, setData] = useState<ChipRaceItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCodes, setSelectedCodes] = useState<Set<string>>(new Set());
  const [lastRefreshTime, setLastRefreshTime] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await marketDataApi.getRaceClose(selectedDate);
      setData(result);
      setTotalPages(Math.ceil(result.length / pageSize));
      
      const now = new Date();
      setLastRefreshTime(`${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`);
    } catch (err) {
      console.error('获取尾盘抢筹数据失败:', err);
      setError('获取数据失败，请稍后重试');
      setData([]);
      setTotalPages(0);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    document.title = '尾盘抢筹 - STOCK';
  }, []);

  useEffect(() => {
    setCurrentPage(1);
    void fetchData();
  }, [selectedDate]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setCurrentPage(1);
    void fetchData();
  };

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  const filteredData = searchKeyword 
    ? data.filter(item => 
        item.code.toLowerCase().includes(searchKeyword.toLowerCase()) ||
        item.name.toLowerCase().includes(searchKeyword.toLowerCase())
      )
    : data;

  const totalFilteredCount = filteredData.length;
  const totalFilteredPages = Math.ceil(totalFilteredCount / pageSize);
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const handleSelectAll = () => {
    if (selectedCodes.size === filteredData.length) {
      setSelectedCodes(new Set());
    } else {
      setSelectedCodes(new Set(filteredData.map(row => row.code)));
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
      ? data.filter(row => selectedCodes.has(row.code))
      : data;

    const headers = COLUMNS.map(col => col.label).join(',');
    const rows = exportList.map(row => {
      return COLUMNS.map(col => {
        const value = row[col.key];
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
    link.setAttribute('download', `race_close_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen space-y-6 p-4 md:p-6 bg-gradient-to-br from-gray-50/50 to-blue-50/30 dark:from-gray-900 dark:to-gray-800">
      <section className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="page-title-icon bg-gradient-to-br from-orange-500/10 to-amber-500/10">
            <TrendingDown className="w-8 h-8 text-orange-500" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              尾盘抢筹数据
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
              尾盘抢筹股票分析，包含抢筹金额、抢筹占比等信息
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
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="input-enhanced w-40"
                  max={getTodayIso()}
                />
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
                disabled={isRefreshing}
              >
                <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
                {isRefreshing ? '刷新中...' : '刷新'}
              </Button>
              {lastRefreshTime && (
                <span className="text-xs text-gray-400">
                  最后刷新: {lastRefreshTime}
                </span>
              )}
              <div className="stat-badge bg-gradient-to-r from-orange-500 to-amber-500 text-white">
                <TrendingDown size={16} className="mr-1" />
                {totalFilteredCount} 条记录
                {searchKeyword && <span className="ml-1 text-xs opacity-75">(筛选后)</span>}
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
            <Button
              variant="primary"
              onClick={handleRefresh}
            >
              重新加载
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <Card padding="none">
            <DataTable
              columns={COLUMNS}
              data={paginatedData}
              loading={isLoading}
              emptyText="暂无数据"
              emptyDescription={searchKeyword ? '没有找到匹配的尾盘抢筹数据' : '没有找到尾盘抢筹数据'}
              rowKey={(row) => row.code}
              linkColumns={['code', 'name']}
              selectedCodes={selectedCodes}
              onSelectAll={handleSelectAll}
              onSelectRow={handleSelectRow}
            />
          </Card>

          {filteredData.length > 0 && totalFilteredPages > 1 && (
            <TablePagination
              currentPage={currentPage}
              totalPages={totalFilteredPages}
              totalCount={totalFilteredCount}
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

export default RaceClosePage;