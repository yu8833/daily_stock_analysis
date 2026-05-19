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
  message?: string;
  is_trading_day?: boolean;
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

type SortField = 'turnover_rate' | 'volume' | 'amount' | 'change_pct';
type SortOrder = 'asc' | 'desc';

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
  
  // 排序状态
  const [sortField, setSortField] = useState<SortField>('change_pct');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // 搜索状态
  const [searchKeyword, setSearchKeyword] = useState('');

  // 提示信息状态
  const [noticeMessage, setNoticeMessage] = useState<string | null>(null);

  const toggleDetail = (code: string) => {
    setExpandedDetails(prev => ({
      ...prev,
      [code]: !prev[code]
    }));
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

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
      if (searchKeyword.trim()) {
        params.append('keyword', searchKeyword.trim());
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
        setTotalPages(result.total_pages);
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
    void fetchLimitUpData();
  }, [selectedDate, pageSize, searchKeyword]);

  useEffect(() => {
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
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none"
                max={getTodayIso()}
              />
              <label className="text-sm text-secondary">关键字</label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="代码/名称/原因..."
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none w-40"
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
                description={noticeMessage || `${selectedDate} 当日没有涨停股票数据，或数据源暂时不可用。`}
                className="border-none bg-transparent px-4 py-8 shadow-none"
              />
            ) : (
              <table className="w-full text-sm">
                <thead className="text-sm text-secondary border-b border-white/10">
                  <tr>
                    <th className="text-left py-3 px-2">代码</th>
                    <th className="text-left py-3 px-2">名称</th>
                    <th className="text-left py-3 px-2">涨停原因</th>
                    <th className="text-left py-3 px-2">详因</th>
                    <th className="text-right py-3 px-2">
                      <button
                        type="button"
                        onClick={() => handleSort('turnover_rate')}
                        className="flex items-center justify-end gap-1 hover:text-primary transition-colors w-full"
                      >
                        换手率
                        {sortField === 'turnover_rate' && (
                          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </button>
                    </th>
                    <th className="text-right py-3 px-2">
                      <button
                        type="button"
                        onClick={() => handleSort('volume')}
                        className="flex items-center justify-end gap-1 hover:text-primary transition-colors w-full"
                      >
                        成交量
                        {sortField === 'volume' && (
                          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </button>
                    </th>
                    <th className="text-right py-3 px-2">
                      <button
                        type="button"
                        onClick={() => handleSort('amount')}
                        className="flex items-center justify-end gap-1 hover:text-primary transition-colors w-full"
                      >
                        成交额(万)
                        {sortField === 'amount' && (
                          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </button>
                    </th>
                    <th className="text-right py-3 px-2">
                      <button
                        type="button"
                        onClick={() => handleSort('change_pct')}
                        className="flex items-center justify-end gap-1 hover:text-primary transition-colors w-full"
                      >
                        涨跌幅
                        {sortField === 'change_pct' && (
                          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
                        )}
                      </button>
                    </th>
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
                      <td className="py-3 px-2 text-secondary max-w-xs" onDoubleClick={() => toggleDetail(stock.code)} title="双击展开详情">
                        <div className="relative cursor-pointer">
                          {(stock.detail_reason?.length || 0) > 50 ? (
                            <>
                              <div className="truncate text-sm" title={stock.detail_reason}>
                                {stock.detail_reason?.slice(0, 50)}...
                              </div>
                              {expandedDetails[stock.code] && (
                                <div className="mt-2 p-2 bg-secondary/10 rounded text-sm whitespace-pre-wrap">
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
