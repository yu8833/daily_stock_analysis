#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===================================
历史数据批量获取工具
===================================

功能：
1. 从选股数据中获取所有股票代码
2. 检查每只股票的历史数据完整性
3. 批量获取缺失的历史数据
4. 实现智能限流，避免触发API限流

限流策略：
- 基础请求间隔：1-3秒随机延迟
- 指数退避：失败后等待时间翻倍
- 请求频率控制：每分钟最多15次请求
- 数据源自动切换失败策略
- 每日请求上限：1000次

断点续传：
- 跳过已有足够数据的股票
- 记录已处理股票到进度文件
- 支持从上次中断处继续

使用方法：
    python scripts/fetch_all_history.py
    python scripts/fetch_all_history.py --start-from 600519
    python scripts/fetch_all_history.py --days 120
"""

import os
import sys

# 设置项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import argparse
import json
import logging
import random
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set

import pandas as pd

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fetch_history.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置参数
BASE_DELAY = 1.0  # 基础延迟（秒）
MAX_DELAY = 5.0   # 最大延迟（秒）
MIN_DELAY = 0.5   # 最小延迟（秒）
MAX_REQUESTS_PER_MINUTE = 15  # 每分钟最大请求数
DAILY_REQUEST_LIMIT = 1000    # 每日请求上限
REQUIRED_RECORDS = 60         # 认为数据足够的最小记录数

# 进度文件路径
PROGRESS_FILE = Path('~/.stock_analysis/fetch_history_progress.json').expanduser()


def setup_django():
    """设置Django环境（如果需要）"""
    try:
        import django
        django.setup()
    except Exception:
        pass


def init_dependencies():
    """初始化依赖项"""
    global get_db, DataFetcherManager, StockSelection, StockDaily
    
    from src.storage import DatabaseManager
    from data_provider import DataFetcherManager
    
    get_db = DatabaseManager.get_instance
    
    from src.storage import StockSelection, StockDaily


class RateLimiter:
    """
    智能限流控制器
    
    功能：
    1. 请求频率控制
    2. 指数退避机制
    3. 每日请求计数
    4. 随机延迟模拟人类行为
    """
    
    def __init__(self):
        self.request_times = []
        self.daily_request_count = 0
        self.last_reset_date = date.today()
        self.backoff_factor = 1
        self.failure_count = 0
        
    def _reset_daily_count(self):
        """重置每日请求计数"""
        today = date.today()
        if today > self.last_reset_date:
            self.daily_request_count = 0
            self.last_reset_date = today
            logger.info("每日请求计数已重置")
    
    def _check_rate_limit(self) -> bool:
        """检查是否超过请求频率限制"""
        now = time.time()
        # 只保留最近1分钟的请求时间
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= MAX_REQUESTS_PER_MINUTE:
            wait_time = 60 - (now - self.request_times[0])
            logger.warning(f"达到每分钟请求上限，等待 {wait_time:.1f} 秒")
            time.sleep(wait_time)
            return True
        return False
    
    def _check_daily_limit(self) -> bool:
        """检查是否超过每日请求上限"""
        self._reset_daily_count()
        if self.daily_request_count >= DAILY_REQUEST_LIMIT:
            logger.error(f"达到每日请求上限 {DAILY_REQUEST_LIMIT}，停止获取")
            return True
        return False
    
    def wait(self, base_delay: float = None):
        """
        执行限流等待
        
        Args:
            base_delay: 基础延迟时间，如果不指定则使用随机延迟
        """
        # 检查频率限制
        self._check_rate_limit()
        
        # 检查每日限制
        if self._check_daily_limit():
            raise StopIteration("达到每日请求上限")
        
        # 计算延迟时间（包含指数退避）
        if base_delay is None:
            delay = random.uniform(MIN_DELAY, BASE_DELAY)
        else:
            delay = base_delay
        
        # 应用指数退避
        delay *= self.backoff_factor
        
        # 限制最大延迟
        delay = min(delay, MAX_DELAY)
        
        if delay > 0:
            logger.debug(f"等待 {delay:.2f} 秒...")
            time.sleep(delay)
        
        # 记录请求时间
        self.request_times.append(time.time())
        self.daily_request_count += 1
    
    def record_success(self):
        """记录成功请求，重置退避因子"""
        self.backoff_factor = 1
        self.failure_count = 0
    
    def record_failure(self):
        """记录失败请求，增加退避因子"""
        self.failure_count += 1
        self.backoff_factor = min(2 ** self.failure_count, 16)
        logger.warning(f"连续失败 {self.failure_count} 次，退避因子: {self.backoff_factor}")


class ProgressTracker:
    """
    进度跟踪器
    
    功能：
    1. 保存已处理股票列表
    2. 记录失败股票列表
    3. 支持断点续传
    4. 统计处理进度
    """
    
    def __init__(self):
        self.processed_codes: Set[str] = set()
        self.failed_codes: Dict[str, str] = {}
        self.start_time = None
        self.total_count = 0
        
        # 创建进度文件目录
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载已保存的进度
        self._load_progress()
    
    def _load_progress(self):
        """加载已保存的进度"""
        if PROGRESS_FILE.exists():
            try:
                with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_codes = set(data.get('processed', []))
                    self.failed_codes = data.get('failed', {})
                    logger.info(f"已加载进度：处理完成 {len(self.processed_codes)} 只，失败 {len(self.failed_codes)} 只")
            except Exception as e:
                logger.warning(f"加载进度失败: {e}")
    
    def _save_progress(self):
        """保存进度到文件"""
        data = {
            'processed': list(self.processed_codes),
            'failed': self.failed_codes,
            'updated_at': datetime.now().isoformat()
        }
        try:
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"保存进度失败: {e}")
    
    def mark_processed(self, code: str):
        """标记股票已处理"""
        self.processed_codes.add(code)
        # 定期保存进度
        if len(self.processed_codes) % 50 == 0:
            self._save_progress()
    
    def mark_failed(self, code: str, reason: str):
        """标记股票处理失败"""
        self.failed_codes[code] = reason
        # 定期保存进度
        if len(self.failed_codes) % 10 == 0:
            self._save_progress()
    
    def is_processed(self, code: str) -> bool:
        """检查股票是否已处理"""
        return code in self.processed_codes
    
    def get_failed_list(self) -> List[str]:
        """获取失败股票列表"""
        return list(self.failed_codes.keys())
    
    def get_progress(self, current: int) -> str:
        """获取进度字符串"""
        if self.total_count == 0:
            return f"{current}/?"
        percentage = (current / self.total_count) * 100
        return f"{current}/{self.total_count} ({percentage:.1f}%)"
    
    def final_save(self):
        """最终保存进度"""
        self._save_progress()
        logger.info(f"处理完成！成功: {len(self.processed_codes)}, 失败: {len(self.failed_codes)}")


def get_stock_codes_from_selection(query_date: date = None) -> List[str]:
    """
    从选股数据中获取所有股票代码
    
    Args:
        query_date: 查询日期，默认今天
    
    Returns:
        股票代码列表
    """
    if query_date is None:
        query_date = datetime.now().date()
    
    db = get_db()
    with db.get_session() as session:
        results = session.execute(
            StockSelection.__table__.select()
            .where(StockSelection.date == query_date)
            .with_only_columns(StockSelection.code)
        ).scalars().all()
    
    codes = [str(c).strip() for c in results if c]
    logger.info(f"从选股数据获取到 {len(codes)} 只股票")
    return codes


def check_history_data(code: str, required_days: int = 60) -> int:
    """
    检查股票的历史数据数量
    
    Args:
        code: 股票代码
        required_days: 认为数据足够的最小天数
    
    Returns:
        现有数据的天数
    """
    from sqlalchemy import func, select
    
    db = get_db()
    with db.get_session() as session:
        result = session.execute(
            select(func.count(StockDaily.id))
            .where(StockDaily.code == code)
        ).scalar()
    
    return result or 0


def fetch_and_save_history(manager, code: str, days: int = 120) -> bool:
    """
    获取股票历史数据并保存到数据库
    
    Args:
        manager: DataFetcherManager实例
        code: 股票代码
        days: 获取天数
    
    Returns:
        是否成功
    """
    try:
        df, source = manager.get_daily_data(code, days=days)
        
        if df is None or df.empty:
            logger.warning(f"获取 {code} 数据为空")
            return False
        
        # 保存到数据库
        save_daily_data(code, df, source)
        logger.info(f"成功获取 {code} 的 {len(df)} 条历史数据 (来源: {source})")
        return True
    
    except Exception as e:
        logger.error(f"获取 {code} 历史数据失败: {e}")
        return False


def save_daily_data(code: str, df: pd.DataFrame, source: str):
    """
    保存日线数据到数据库
    
    Args:
        code: 股票代码
        df: 日线数据DataFrame
        source: 数据来源
    """
    from sqlalchemy import select
    
    db = get_db()
    
    with db.get_session() as session:
        for _, row in df.iterrows():
            try:
                # 检查是否已存在
                existing = session.execute(
                    select(StockDaily)
                    .where(StockDaily.code == code)
                    .where(StockDaily.date == row['date'])
                ).scalar_one_or_none()
                
                if existing:
                    # 更新现有记录
                    existing.open = row.get('open')
                    existing.high = row.get('high')
                    existing.low = row.get('low')
                    existing.close = row.get('close')
                    existing.volume = row.get('volume')
                    existing.amount = row.get('amount')
                    existing.pct_chg = row.get('pct_chg')
                    existing.ma5 = row.get('ma5')
                    existing.ma10 = row.get('ma10')
                    existing.ma20 = row.get('ma20')
                    existing.volume_ratio = row.get('volume_ratio')
                    existing.data_source = source
                else:
                    # 创建新记录
                    daily_data = StockDaily(
                        code=code,
                        date=row['date'],
                        open=row.get('open'),
                        high=row.get('high'),
                        low=row.get('low'),
                        close=row.get('close'),
                        volume=row.get('volume'),
                        amount=row.get('amount'),
                        pct_chg=row.get('pct_chg'),
                        ma5=row.get('ma5'),
                        ma10=row.get('ma10'),
                        ma20=row.get('ma20'),
                        volume_ratio=row.get('volume_ratio'),
                        data_source=source
                    )
                    session.add(daily_data)
            
            except Exception as e:
                logger.debug(f"保存 {code} {row['date']} 失败: {e}")
        
        session.commit()


def should_fetch(code: str, required_days: int, progress: ProgressTracker) -> bool:
    """
    判断是否需要获取该股票的历史数据
    
    Args:
        code: 股票代码
        required_days: 需要的最小天数
        progress: 进度跟踪器
    
    Returns:
        是否需要获取
    """
    # 检查是否已处理过
    if progress.is_processed(code):
        logger.debug(f"{code} 已处理过，跳过")
        return False
    
    # 检查现有数据量
    existing_days = check_history_data(code, required_days)
    if existing_days >= required_days:
        logger.debug(f"{code} 已有 {existing_days} 天数据，足够，跳过")
        progress.mark_processed(code)
        return False
    
    return True


def main(days: int = 120, start_from: Optional[str] = None):
    """
    主函数：批量获取所有股票的历史数据
    
    Args:
        days: 获取历史数据的天数
        start_from: 从指定股票代码开始（用于断点续传）
    """
    logger.info("=" * 60)
    logger.info("开始批量获取历史数据")
    logger.info(f"获取天数: {days}")
    logger.info(f"从股票: {start_from or '从头开始'}")
    logger.info("=" * 60)
    
    # 初始化依赖
    init_dependencies()
    
    # 创建进度跟踪器
    progress = ProgressTracker()
    
    # 创建限流控制器
    rate_limiter = RateLimiter()
    
    # 获取股票列表
    stock_codes = get_stock_codes_from_selection()
    progress.total_count = len(stock_codes)
    
    # 如果指定了起始股票，找到其位置
    start_index = 0
    if start_from:
        try:
            start_index = stock_codes.index(start_from)
            logger.info(f"从第 {start_index} 只股票 {start_from} 开始")
        except ValueError:
            logger.warning(f"未找到股票 {start_from}，从头开始")
    
    # 统计变量
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    # 初始化数据获取管理器（只初始化一次）
    logger.info("初始化数据获取管理器...")
    manager = DataFetcherManager()
    logger.info("数据获取管理器初始化完成")
    
    # 主循环
    for i, code in enumerate(stock_codes[start_index:], start=start_index):
        try:
            # 检查是否需要获取
            if not should_fetch(code, REQUIRED_RECORDS, progress):
                skipped_count += 1
                continue
            
            # 限流等待
            rate_limiter.wait()
            
            # 获取历史数据
            logger.info(f"[{progress.get_progress(i+1)}] 正在获取 {code} 的历史数据...")
            
            success = fetch_and_save_history(manager, code, days)
            
            if success:
                success_count += 1
                rate_limiter.record_success()
                progress.mark_processed(code)
            else:
                failed_count += 1
                rate_limiter.record_failure()
                progress.mark_failed(code, "获取数据失败")
            
            # 输出进度
            if (i + 1) % 10 == 0:
                logger.info(f"进度: {progress.get_progress(i+1)} | 成功: {success_count} | 失败: {failed_count} | 跳过: {skipped_count}")
            
            # 随机额外延迟（模拟人类行为）
            if random.random() > 0.7:
                extra_delay = random.uniform(0.5, 1.5)
                time.sleep(extra_delay)
        
        except StopIteration:
            logger.info("达到每日请求上限，停止获取")
            break
        except Exception as e:
            logger.error(f"处理 {code} 时发生异常: {e}")
            failed_count += 1
            progress.mark_failed(code, str(e))
    
    # 最终保存进度
    progress.final_save()
    
    # 输出统计结果
    logger.info("=" * 60)
    logger.info("批量获取历史数据完成")
    logger.info(f"总股票数: {len(stock_codes)}")
    logger.info(f"成功获取: {success_count}")
    logger.info(f"获取失败: {failed_count}")
    logger.info(f"跳过(已有数据): {skipped_count}")
    logger.info("=" * 60)
    
    # 如果有失败的股票，列出它们
    if failed_count > 0:
        logger.info("失败的股票列表:")
        for code, reason in progress.failed_codes.items():
            logger.info(f"  {code}: {reason}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量获取股票历史数据')
    parser.add_argument('--days', type=int, default=120, help='获取历史数据的天数')
    parser.add_argument('--start-from', type=str, default=None, help='从指定股票代码开始')
    
    args = parser.parse_args()
    
    main(days=args.days, start_from=args.start_from)