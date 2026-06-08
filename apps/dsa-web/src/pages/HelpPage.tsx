import type React from 'react';
import { MessageSquareQuote, TrendingUp, ArrowUpCircle, ArrowDownCircle, BarChart3, HelpCircle } from 'lucide-react';
import { Card } from '../components/common';

const HelpPage: React.FC = () => {
  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex items-center gap-3">
        <HelpCircle className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-semibold text-foreground">系统说明</h1>
          <p className="text-sm text-secondary-text">了解 Daily Stock Analysis 的主要功能</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* 问股 */}
        <Card className="flex flex-col">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
              <MessageSquareQuote className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2 text-lg font-medium text-foreground">问股</h3>
              <div className="space-y-2 text-sm text-secondary-text">
                <p>基于 AI 的智能股票分析功能，支持多种分析策略。</p>
                <ul className="ml-4 list-disc space-y-1">
                  <li>输入股票代码或名称开始分析</li>
                  <li>选择合适的分析策略（默认推荐全面分析）</li>
                  <li>AI 会结合多种因素给出综合分析报告</li>
                  <li>支持实时问股和历史分析记录</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* 选股 */}
        <Card className="flex flex-col">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2 text-lg font-medium text-foreground">选股</h3>
              <div className="space-y-2 text-sm text-secondary-text">
                <p>多策略智能选股，帮助你发现潜在的投资机会。</p>
                <ul className="ml-4 list-disc space-y-1">
                  <li>支持多种选股策略组合</li>
                  <li>基于技术指标和形态识别</li>
                  <li>自定义筛选条件</li>
                  <li>查看选股历史和结果导出</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* 买入信号 */}
        <Card className="flex flex-col">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100">
              <ArrowUpCircle className="h-6 w-6 text-green-600" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2 text-lg font-medium text-foreground">买入信号</h3>
              <div className="space-y-2 text-sm text-secondary-text">
                <p>实时监控股票买入机会，基于技术分析的信号系统。</p>
                <ul className="ml-4 list-disc space-y-1">
                  <li>实时推送买入信号</li>
                  <li>多种技术指标综合判断</li>
                  <li>信号历史记录和回溯</li>
                  <li>自定义信号强度阈值</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* 卖出信号 */}
        <Card className="flex flex-col">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100">
              <ArrowDownCircle className="h-6 w-6 text-red-600" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2 text-lg font-medium text-foreground">卖出信号</h3>
              <div className="space-y-2 text-sm text-secondary-text">
                <p>识别股票卖出时机，帮助你锁定利润或止损。</p>
                <ul className="ml-4 list-disc space-y-1">
                  <li>实时推送卖出信号</li>
                  <li>趋势反转和技术背离识别</li>
                  <li>结合量价分析判断</li>
                  <li>风险预警和建议</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>

        {/* 涨停 */}
        <Card className="flex flex-col md:col-span-2">
          <div className="flex items-start gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-yellow-100">
              <BarChart3 className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="flex-1">
              <h3 className="mb-2 text-lg font-medium text-foreground">涨停</h3>
              <div className="space-y-2 text-sm text-secondary-text">
                <p>每日涨停股票分析，了解市场热点和情绪。</p>
                <ul className="ml-4 list-disc space-y-1">
                  <li>查看当日涨停股票列表</li>
                  <li>涨停原因分类统计</li>
                  <li>成交额和换手率分析</li>
                  <li>历史数据对比</li>
                </ul>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <Card className="mt-4">
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100">
            <HelpCircle className="h-6 w-6 text-blue-600" />
          </div>
          <div className="flex-1">
            <h3 className="mb-2 text-lg font-medium text-foreground">更多文档</h3>
            <div className="space-y-2 text-sm text-secondary-text">
              <p>如需了解更多详细信息，请访问：</p>
              <a 
                href="/docs" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="inline-flex items-center gap-1 text-primary hover:text-primary/80 transition-colors"
              >
                <HelpCircle className="h-4 w-4" />
                <span>查看完整文档</span>
              </a>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default HelpPage;
