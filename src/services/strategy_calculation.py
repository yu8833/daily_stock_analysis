# -*- coding: utf-8 -*-
"""
===================================
策略计算服务
===================================

职责：
1. 异步计算需要历史数据的策略信号
2. 分批处理股票，避免触发数据源频率限制
3. 更新数据库中的策略字段
"""

import logging
import time
from datetime import date, datetime
from typing import List, Dict, Any, Optional

import pandas as pd

from data_provider import DataFetcherManager
from src.storage import DatabaseManager, StockSelection
from strategy import (
    parking_apron_check,
    low_backtrace_increase_check,
    turtle_trade_check,
    check_high_tight,
    check_low_increase,
)

logger = logging.getLogger(__name__)


class StrategyCalculationService:
    """策略计算服务"""

    def __init__(self):
        self.data_fetcher = DataFetcherManager()
        self.db = DatabaseManager()
        # 控制请求频率，避免触发限制
        self.request_delay = 1.0  # 每次请求间隔（秒）
        self.batch_size = 10  # 每批处理股票数量

    def calculate_strategies_for_date(self, query_date: date) -> Dict[str, int]:
        """
        为指定日期的所有股票计算策略信号
        
        Args:
            query_date: 查询日期
            
        Returns:
            统计结果字典
        """
        logger.info(f"[StrategyService] 开始计算 {query_date} 的策略信号")
        
        # 获取需要处理的股票列表
        stock_codes = self._get_stock_codes_for_date(query_date)
        if not stock_codes:
            logger.info(f"[StrategyService] 未找到 {query_date} 的股票数据")
            return {"total": 0, "updated": 0, "failed": 0}
        
        logger.info(f"[StrategyService] 共 {len(stock_codes)} 只股票需要处理")
        
        updated_count = 0
        failed_count = 0
        
        # 分批处理
        for i in range(0, len(stock_codes), self.batch_size):
            batch = stock_codes[i:i+self.batch_size]
            logger.info(f"[StrategyService] 处理批次 {i//self.batch_size + 1}: {len(batch)} 只股票")
            
            for stock_code in batch:
                try:
                    success = self._calculate_and_update(query_date, stock_code)
                    if success:
                        updated_count += 1
                    else:
                        failed_count += 1
                    
                    # 控制请求频率
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    logger.error(f"[StrategyService] 处理股票 {stock_code} 失败: {e}")
                    failed_count += 1
        
        logger.info(f"[StrategyService] 策略计算完成: 总计 {len(stock_codes)} 只, 更新 {updated_count} 只, 失败 {failed_count} 只")
        
        return {
            "total": len(stock_codes),
            "updated": updated_count,
            "failed": failed_count
        }

    def _get_stock_codes_for_date(self, query_date: date) -> List[str]:
        """获取指定日期的股票代码列表"""
        try:
            with self.db.get_session() as session:
                results = session.execute(
                    session.query(StockSelection.code)
                    .filter(StockSelection.date == query_date)
                ).scalars().all()
                return [str(code).strip() for code in results if code]
        except Exception as e:
            logger.error(f"[StrategyService] 获取股票列表失败: {e}")
            return []

    def _calculate_and_update(self, query_date: date, stock_code: str) -> bool:
        """
        为单只股票计算策略并更新数据库
        
        Args:
            query_date: 查询日期
            stock_code: 股票代码
            
        Returns:
            是否成功更新
        """
        try:
            # 获取历史数据
            stock_data = self.data_fetcher.get_daily_data(stock_code, days=120)
            if stock_data is None:
                logger.debug(f"[StrategyService] 股票 {stock_code} 未获取到历史数据")
                return False
            
            # 处理返回值
            if isinstance(stock_data, tuple):
                df = stock_data[0]
            else:
                df = stock_data
            
            if df is None or df.empty:
                logger.debug(f"[StrategyService] 股票 {stock_code} 历史数据为空")
                return False
            
            code_name = (query_date.strftime('%Y-%m-%d'), stock_code)
            
            # 计算需要历史数据的策略
            strategies = {}
            
            try:
                strategies['parking_apron'] = parking_apron_check(code_name, df)
            except Exception as e:
                logger.debug(f"[StrategyService] 股票 {stock_code} 停机坪策略计算失败: {e}")
                strategies['parking_apron'] = None
            
            try:
                strategies['low_backtrace_increase'] = low_backtrace_increase_check(code_name, df)
            except Exception as e:
                logger.debug(f"[StrategyService] 股票 {stock_code} 无大幅回撤策略计算失败: {e}")
                strategies['low_backtrace_increase'] = None
            
            try:
                strategies['turtle_trade'] = turtle_trade_check(code_name, df)
            except Exception as e:
                logger.debug(f"[StrategyService] 股票 {stock_code} 海龟交易法则计算失败: {e}")
                strategies['turtle_trade'] = None
            
            try:
                strategies['high_tight_flag'] = check_high_tight(code_name, df)
            except Exception as e:
                logger.debug(f"[StrategyService] 股票 {stock_code} 宽而窄的旗形策略计算失败: {e}")
                strategies['high_tight_flag'] = None
            
            try:
                strategies['low_atr_growth'] = check_low_increase(code_name, df)
            except Exception as e:
                logger.debug(f"[StrategyService] 股票 {stock_code} 低ATR成长策略计算失败: {e}")
                strategies['low_atr_growth'] = None
            
            # 更新数据库
            with self.db.get_session() as session:
                record = session.query(StockSelection).filter(
                    StockSelection.date == query_date,
                    StockSelection.code == stock_code
                ).first()
                
                if record:
                    for key, value in strategies.items():
                        setattr(record, key, "是" if value else "否")
                    
                    session.commit()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"[StrategyService] 处理股票 {stock_code} 异常: {e}")
            return False


def run_strategy_calculation(query_date: date) -> Dict[str, int]:
    """
    执行策略计算任务（用于后台任务调用）
    
    Args:
        query_date: 查询日期
        
    Returns:
        统计结果
    """
    service = StrategyCalculationService()
    return service.calculate_strategies_for_date(query_date)