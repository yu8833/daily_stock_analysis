import React, { useEffect, useState } from 'react';
import { Card, Badge } from '../components/common';
import { BarChart3 } from 'lucide-react';

interface PatternInfo {
  key: string;
  cn: string;
  en: string;
}

interface PatternItem {
  code: string;
  name: string;
  pattern_key: string;
  pattern_cn: string;
  pattern_en: string;
  direction: string;
  date: string;
  position: number;
}

const PatternPage: React.FC = () => {
  const [patternList, setPatternList] = useState<PatternInfo[]>([]);
  const [stockCode, setStockCode] = useState('600519');
  const [patterns, setPatterns] = useState<PatternItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPatterns, setSelectedPatterns] = useState<Set<string>>(new Set());
  const [directionFilter, setDirectionFilter] = useState<'all' | 'up' | 'down'>('all');

  useEffect(() => {
    fetchPatternList();
  }, []);

  const fetchPatternList = async () => {
    try {
      const response = await fetch('/api/v1/pattern/list');
      const data = await response.json();
      setPatternList(data.patterns || []);
      setSelectedPatterns(new Set(data.patterns?.map((p: PatternInfo) => p.key) || []));
    } catch (err) {
      console.error('获取形态列表失败:', err);
    }
  };

  const handleSearch = async () => {
    if (!stockCode.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/pattern/${stockCode.trim()}`);
      const data = await response.json();

      if (data.error === 'dependency_missing') {
        setError('talib库未安装，无法进行K线形态识别');
        setPatterns([]);
      } else if (data.error) {
        setError(data.message || '获取K线形态失败');
        setPatterns([]);
      } else {
        setPatterns(data.patterns || []);
      }
    } catch (err) {
      console.error('获取K线形态失败:', err);
      setError('获取K线形态失败，请稍后重试');
      setPatterns([]);
    } finally {
      setIsLoading(false);
    }
  };

  const togglePattern = (key: string) => {
    const newSelected = new Set(selectedPatterns);
    if (newSelected.has(key)) {
      newSelected.delete(key);
    } else {
      newSelected.add(key);
    }
    setSelectedPatterns(newSelected);
  };

  const selectAll = () => {
    setSelectedPatterns(new Set(patternList.map(p => p.key)));
  };

  const selectNone = () => {
    setSelectedPatterns(new Set());
  };

  const filteredPatterns = patterns.filter(p => {
    if (!selectedPatterns.has(p.pattern_key)) return false;
    if (directionFilter === 'up' && p.direction !== '看涨') return false;
    if (directionFilter === 'down' && p.direction !== '看跌') return false;
    return true;
  });

  return (
    <div className="min-h-screen space-y-6 p-4 md:p-6 bg-gradient-to-br from-gray-50/50 to-purple-50/30 dark:from-gray-900 dark:to-gray-800">
      <section className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="page-title-icon bg-gradient-to-br from-blue-500/10 to-cyan-500/10">
            <BarChart3 className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              K线形态
            </h1>
            <p className="text-sm md:text-base text-gray-600 dark:text-gray-400 mt-1">
              基于Talib的股票K线形态识别，支持60+种经典形态
            </p>
          </div>
        </div>
      </section>

      <Card>
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">股票代码:</span>
              <input
                type="text"
                value={stockCode}
                onChange={(e) => setStockCode(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="请输入股票代码"
                className="input-enhanced pl-3 pr-8 w-40"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isLoading}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {isLoading ? '分析中...' : '分析'}
            </button>
          </div>

          {error && (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {patterns.length > 0 && (
            <div className="flex flex-wrap gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">形态筛选:</span>
                <button
                  onClick={selectAll}
                  className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                >
                  全选
                </button>
                <button
                  onClick={selectNone}
                  className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  全不选
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">方向:</span>
                <select
                  value={directionFilter}
                  onChange={(e) => setDirectionFilter(e.target.value as 'all' | 'up' | 'down')}
                  className="input-enhanced h-8 text-xs"
                >
                  <option value="all">全部</option>
                  <option value="up">只看涨</option>
                  <option value="down">只看跌</option>
                </select>
              </div>
            </div>
          )}

          {patterns.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {patternList.map(pattern => (
                <button
                  key={pattern.key}
                  onClick={() => togglePattern(pattern.key)}
                  className={`px-2 py-1 text-xs rounded-full transition-colors ${
                    selectedPatterns.has(pattern.key)
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title={pattern.en}
                >
                  {pattern.cn}
                </button>
              ))}
            </div>
          )}
        </div>
      </Card>

      {filteredPatterns.length > 0 && (
        <Card>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              识别结果 ({filteredPatterns.length}个形态)
            </h2>
            <div className="flex gap-4 text-sm">
              <span className="text-green-600 dark:text-green-400">
                看涨: {filteredPatterns.filter(p => p.direction === '看涨').length}
              </span>
              <span className="text-red-600 dark:text-red-400">
                看跌: {filteredPatterns.filter(p => p.direction === '看跌').length}
              </span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-100 dark:divide-gray-700">
              <thead>
                <tr className="table-header-cell">
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    日期
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    形态
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    方向
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    英文名
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-700">
                {filteredPatterns.map((pattern, index) => (
                  <tr key={`${pattern.date}-${pattern.pattern_key}-${index}`} className="table-row">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {pattern.date}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <Badge variant={pattern.direction === '看涨' ? 'success' : 'danger'}>
                        {pattern.pattern_cn}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`text-sm font-medium ${
                        pattern.direction === '看涨'
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {pattern.direction}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {pattern.pattern_en}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {patterns.length > 0 && filteredPatterns.length === 0 && (
        <Card>
          <div className="text-center py-8">
            <p className="text-gray-500 dark:text-gray-400">
              没有符合条件的形态，请调整筛选条件
            </p>
          </div>
        </Card>
      )}

      {patterns.length === 0 && !isLoading && !error && (
        <Card>
          <div className="text-center py-12">
            <BarChart3 className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              K线形态识别
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              输入股票代码，点击"分析"按钮获取K线形态识别结果
            </p>
            <div className="text-left max-w-2xl mx-auto p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">支持的K线形态包括：</h4>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>反转形态：锤头、射击之星、吞没模式、十字星等</li>
                <li>持续形态：三个白兵、旗帜形、三角形等</li>
                <li>顶部形态：乌云压顶、暮星、三只乌鸦等</li>
                <li>底部形态：晨星、锤头、刺透形态等</li>
              </ul>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default PatternPage;