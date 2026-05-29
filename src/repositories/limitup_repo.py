# -*- coding: utf-8 -*-
"""
===================================
涨停数据访问层
===================================

职责：
1. 封装涨停原因数据的数据库操作
2. 提供涨停数据查询接口
3. 支持数据持久化和缓存
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any

import pandas as pd
from sqlalchemy import select, and_, desc, delete

from src.storage import DatabaseManager, StockLimitupReason
from data_provider.jqka_fetcher import TenJqkaFetcher

logger = logging.getLogger(__name__)


class LimitUpRepository:
    """
    涨停数据访问层
    
    封装 StockLimitupReason 表的数据库操作，支持从数据源获取并持久化
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        初始化数据访问层
        
        Args:
            db_manager: 数据库管理器（可选，默认使用单例）
        """
        self.db = db_manager or DatabaseManager.get_instance()
        self.fetcher = TenJqkaFetcher()
    
    def get_by_date(self, query_date: date) -> List[StockLimitupReason]:
        """
        获取指定日期的涨停数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            StockLimitupReason 对象列表
        """
        with self.db.get_session() as session:
            results = session.execute(
                select(StockLimitupReason)
                .where(StockLimitupReason.date == query_date)
                .order_by(desc(StockLimitupReason.change_rate), StockLimitupReason.code)
            ).scalars().all()
            return list(results)
    
    def get_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[StockLimitupReason]:
        """
        获取指定日期范围的涨停数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            StockLimitupReason 对象列表
        """
        with self.db.get_session() as session:
            results = session.execute(
                select(StockLimitupReason)
                .where(and_(
                    StockLimitupReason.date >= start_date,
                    StockLimitupReason.date <= end_date
                ))
                .order_by(desc(StockLimitupReason.date), desc(StockLimitupReason.change_rate))
            ).scalars().all()
            return list(results)
    
    def get_by_code(self, code: str, days: int = 30) -> List[StockLimitupReason]:
        """
        获取指定股票的涨停历史
        
        Args:
            code: 股票代码
            days: 最近天数
            
        Returns:
            StockLimitupReason 对象列表
        """
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockLimitupReason)
                .where(and_(
                    StockLimitupReason.code == code,
                    StockLimitupReason.date >= cutoff_date.date()
                ))
                .order_by(desc(StockLimitupReason.date))
            ).scalars().all()
            return list(results)
    
    def has_date_data(self, query_date: date) -> bool:
        """
        检查指定日期是否已有数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            是否存在数据
        """
        with self.db.get_session() as session:
            result = session.execute(
                select(StockLimitupReason)
                .where(StockLimitupReason.date == query_date)
            ).scalar_one_or_none()
            return result is not None
    
    def save_from_fetcher(self, query_date: date) -> int:
        """
        从数据源获取数据并保存到数据库

        Args:
            query_date: 查询日期

        Returns:
            保存的记录数
        """
        # 从同花顺获取数据
        data_list = self.fetcher.get_limit_up_reason(query_date.strftime('%Y-%m-%d'))

        if not data_list:
            logger.info(f"未获取到 {query_date} 的涨停数据")
            return 0

        # 检查返回数据的日期是否与查询日期匹配
        # 同花顺API在当天数据未发布时可能返回昨日数据，需要过滤
        data_date_str = data_list[0].get('日期', '')
        if data_date_str:
            try:
                data_date = datetime.strptime(str(data_date_str), '%Y-%m-%d').date()
                if data_date != query_date:
                    logger.info(
                        f"数据日期不匹配: 请求 {query_date}, 返回 {data_date}。"
                        f"当日数据可能尚未发布，返回空数据"
                    )
                    return 0
            except ValueError:
                logger.warning(f"无法解析数据日期: {data_date_str}，跳过日期校验")

        # 删除该日期的旧数据
        self._delete_date_data(query_date)

        # 插入新数据
        saved_count = 0
        with self.db.get_session() as session:
            for item in data_list:
                try:
                    record = StockLimitupReason(
                        date=query_date,
                        code=str(item.get('代码', '')).strip(),
                        name=str(item.get('名称', '')).strip(),
                        title=str(item.get('原因', '')).strip(),
                        reason=str(item.get('详因', '')).strip(),
                        new_price=item.get('最新价'),
                        change_rate=item.get('涨跌幅'),
                        ups_downs=item.get('涨跌额'),
                        turnoverrate=item.get('换手率'),
                        volume=item.get('成交量'),
                        deal_amount=item.get('成交额'),
                        dde=item.get('DDE'),
                    )
                    session.add(record)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"保存涨停数据失败 (code={item.get('代码')}): {e}")

            session.commit()
            logger.info(f"保存涨停数据成功: {query_date}, 新增 {saved_count} 条")

        return saved_count
    
    def _delete_date_data(self, query_date: date) -> None:
        """
        删除指定日期的数据
        
        Args:
            query_date: 查询日期
        """
        with self.db.get_session() as session:
            session.execute(
                delete(StockLimitupReason)
                .where(StockLimitupReason.date == query_date)
            )
            session.commit()
    
    def _has_missing_fields(self, record: StockLimitupReason) -> bool:
        """
        检查单条记录是否有缺失的关键字段
        
        Args:
            record: StockLimitupReason 对象
            
        Returns:
            是否有缺失字段
        """
        if record.turnoverrate is None or (isinstance(record.turnoverrate, float) and record.turnoverrate == 0.0):
            return True
        if record.volume is None or (isinstance(record.volume, float) and record.volume == 0.0):
            return True
        if record.deal_amount is None or (isinstance(record.deal_amount, float) and record.deal_amount == 0.0):
            return True
        if record.change_rate is None or (isinstance(record.change_rate, float) and record.change_rate == 0.0):
            return True
        
        return False
    
    def get_or_fetch(self, query_date: date, check_missing: bool = False) -> List[StockLimitupReason]:
        """
        获取指定日期的涨停数据，如果数据库中没有则从数据源获取并保存
        
        Args:
            query_date: 查询日期
            check_missing: 是否检查缺失字段，True时如果有缺失会删除旧数据并重新获取
            
        Returns:
            StockLimitupReason 对象列表
        """
        # 先检查数据库
        results = self.get_by_date(query_date)
        if results:
            if check_missing:
                # 检查是否有缺失字段的记录
                has_missing = any(self._has_missing_fields(r) for r in results)
                if has_missing:
                    # 有缺失字段，删除旧数据并重新获取
                    logger.info(f"发现 {query_date} 的涨停数据有缺失字段，删除旧数据并重新获取")
                    self._delete_date_data(query_date)
                    self.save_from_fetcher(query_date)
                    # 返回重新获取的数据
                    return self.get_by_date(query_date)
            
            logger.debug(f"从数据库获取涨停数据: {query_date}, {len(results)} 条")
            return results
        
        # 数据库没有，从数据源获取
        logger.info(f"数据库未找到 {query_date} 的涨停数据，从数据源获取")
        self.save_from_fetcher(query_date)
        
        # 返回获取的数据
        return self.get_by_date(query_date)
    
    def batch_fetch_and_save(self, dates: List[date]) -> Dict[date, int]:
        """
        批量获取并保存多个日期的涨停数据
        
        Args:
            dates: 日期列表
            
        Returns:
            每个日期保存的记录数字典
        """
        result = {}
        for query_date in dates:
            count = self.save_from_fetcher(query_date)
            result[query_date] = count
        return result
