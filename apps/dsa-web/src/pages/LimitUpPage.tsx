import type React from 'react';
import { useEffect, useState } from 'react';
import { Card, Badge, EmptyState, Loading } from '../components/common';
import { toDateInputValue } from '../utils/format';
import { TrendingUp } from 'lucide-react';

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

interface ExpandedDetail {
  [key: string]: boolean;
}

interface LimitUpResponse {
  date: string;
  count: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  data: LimitUpStock[];
}

function getTodayIso(): string {
  return toDateInputValue(new Date());
}

function formatNumber(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return '--';
  return Number(value).toLocaleString('zh-CN');
}

function formatMoney(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return '--';
  return `${Number(value).toLocaleString('zh-CN')}`;
}

function formatPct(value: number | null | undefined): string {
  if (value == null || Number.isNaN(value)) return '--';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

const LimitUpPage: React.FC = () => {
  useEffect(() => {
    document.title = '涨停揭秘 - STOCK';
  }, []);

  const [selectedDate, setSelectedDate] = useState(getTodayIso());
  const [stockList, setStockList] = useState<LimitUpStock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedDetails, setExpandedDetails] = useState<ExpandedDetail>({});
  
  // 分页状态
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const toggleDetail = (code: string) => {
    setExpandedDetails(prev => ({
      ...prev,
      [code]: !prev[code]
    }));
  };

  const fetchLimitUpData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const url = `/api/v1/limitup/?date=${selectedDate}&page=${currentPage}&page_size=${pageSize}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('获取数据失败');
      }

      const result: LimitUpResponse = await response.json();

      if (result.data && Array.isArray(result.data)) {
        setStockList(result.data);
        setTotalCount(result.count);
        setTotalPages(result.total_pages);
      } else {
        setStockList([]);
        setTotalCount(0);
        setTotalPages(0);
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
    void fetchLimitUpData();
  }, [selectedDate, pageSize]);

  useEffect(() => {
    void fetchLimitUpData();
  }, [currentPage]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
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
            <div className="flex items-center gap-2">
              <label className="text-sm text-secondary">选择日期</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none"
                max={getTodayIso()}
              />
            </div>
            <Badge variant="success">{totalCount} 只涨停</Badge>
          </div>
        </Card>
      </section>

      {error ? (
        <Card padding="md">
          <div className="text-center py-8">
            <p className="text-danger">{error}</p>
            <button
              type="button"
              className="btn-secondary mt-3"
              onClick={() => void fetchLimitUpData()}
            >
              重试
            </button>
          </div>
        </Card>
      ) : (
        <Card padding="md">
          <div className="overflow-x-auto">
            {isLoading ? (
              <div className="flex justify-center py-12">
                <Loading label="获取涨停数据中..." />
              </div>
            ) : stockList.length === 0 ? (
              <EmptyState
                title="暂无涨停数据"
                description={`${selectedDate} 当日没有涨停股票数据，或数据源暂时不可用。`}
                className="border-none bg-transparent px-4 py-8 shadow-none"
              />
            ) : (
              <table className="w-full text-sm">
                <thead className="text-xs text-secondary border-b border-white/10">
                  <tr>
                    <th className="text-left py-3 px-2">代码</th>
                    <th className="text-left py-3 px-2">名称</th>
                    <th className="text-left py-3 px-2">涨停原因</th>
                    <th className="text-left py-3 px-2">详因</th>
                    <th className="text-right py-3 px-2">换手率</th>
                    <th className="text-right py-3 px-2">成交量</th>
                    <th className="text-right py-3 px-2">成交额(万)</th>
                    <th className="text-right py-3 px-2">涨跌幅</th>
                  </tr>
                </thead>
                <tbody>
                  {stockList.map((stock, index) => (
                    <tr key={`${stock.code}-${index}`} className="border-b border-white/5 hover:bg-white/[0.02]">
                      <td className="py-3 px-2 font-mono text-foreground">{stock.code}</td>
                      <td className="py-3 px-2 font-medium">{stock.name}</td>
                      <td className="py-3 px-2 text-secondary max-w-xs truncate" title={stock.reason}>
                        {stock.reason || '-'}
                      </td>
                      <td className="py-3 px-2 text-secondary max-w-xs">
                        <div className="relative">
                          {(stock.detail_reason?.length || 0) > 50 ? (
                            <>
                              <div className="truncate text-sm" title={stock.detail_reason}>
                                {stock.detail_reason?.slice(0, 50)}...
                              </div>
                              <button
                                type="button"
                                onClick={() => toggleDetail(stock.code)}
                                className="mt-1 text-sm text-primary hover:text-primary/80 hover:text-sm"
                              >
                                {expandedDetails[stock.code] ? '收起' : '展开'}
                              </button>
                              {expandedDetails[stock.code] && (
                                <div className="mt-2 p-2 bg-secondary/10 rounded text-sm whitespace-pre-wrap hover:text-sm">
                                  {stock.detail_reason}
                                </div>
                              )}
                            </>
                          ) : (
                            <span className="text-sm" title={stock.detail_reason}>{stock.detail_reason || '-'}</span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-2 text-right text-secondary">
                        {stock.turnover_rate != null ? `${stock.turnover_rate}%` : '-'}
                      </td>
                      <td className="py-3 px-2 text-right text-secondary">
                        {formatNumber(stock.volume)}
                      </td>
                      <td className="py-3 px-2 text-right text-secondary">
                        {formatMoney(stock.amount)}
                      </td>
                      <td className={`py-3 px-2 text-right font-medium ${stock.change_pct != null && stock.change_pct > 0 ? 'text-success' : 'text-secondary'}`}>
                        {formatPct(stock.change_pct)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          
          {/* 分页组件 */}
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
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = currentPage <= 3 ? i + 1 : 
                                 currentPage + i - 2 > totalPages ? totalPages - 4 + i : 
                                 currentPage + i - 2;
                  return (
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
                  );
                })}
                
                <button
                  type="button"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn-secondary h-8 px-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default LimitUpPage;
