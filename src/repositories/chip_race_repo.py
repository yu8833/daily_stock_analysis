# -*- coding: utf-8 -*-
"""
===================================
ChipRaceRepository - 抢筹数据访问层
===================================

处理早盘抢筹和尾盘抢筹数据的数据库操作
"""

import logging
from datetime import date, datetime
from typing import List, Optional

import pandas as pd

from src.storage import DatabaseManager, StockChipRace
from data_provider import ChipRaceFetcher

logger = logging.getLogger(__name__)


class ChipRaceRepository:
    """
    抢筹数据访问层
    
    提供早盘抢筹和尾盘抢筹数据的存储和查询方法
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager.get_instance()
        self.fetcher = ChipRaceFetcher()
    
    def save_chip_race_open(self, df: pd.DataFrame, query_date: Optional[date] = None) -> int:
        """
        保存早盘抢筹数据
        
        Args:
            df: 早盘抢筹数据 DataFrame
            query_date: 查询日期
            
        Returns:
            保存的记录数
        """
        if df.empty:
            return 0
        
        records = []
        save_date = query_date or date.today()
        
        for _, row in df.iterrows():
            record = StockChipRace(
                code=row["代码"],
                name=row["名称"],
                date=save_date,
                period=0,  # 0=早盘
                latest_price=row["最新价"],
                change_pct=row["涨跌幅"],
                prev_close=row["昨收"],
                open_price=row["今开"],
                amount=row["开盘金额"],
                race_amount=row["抢筹成交金额"],
                race_ratio=row["抢筹占比"],
                race_pct=row["抢筹幅度"],
                board_days=row["天"],
                board_type=row["板"],
                created_at=datetime.now(),
            )
            records.append(record)
        
        return self._save_records(records)
    
    def save_chip_race_close(self, df: pd.DataFrame, query_date: Optional[date] = None) -> int:
        """
        保存尾盘抢筹数据
        
        Args:
            df: 尾盘抢筹数据 DataFrame
            query_date: 查询日期
            
        Returns:
            保存的记录数
        """
        if df.empty:
            return 0
        
        records = []
        save_date = query_date or date.today()
        
        for _, row in df.iterrows():
            record = StockChipRace(
                code=row["代码"],
                name=row["名称"],
                date=save_date,
                period=1,  # 1=尾盘
                latest_price=row["最新价"],
                change_pct=row["涨跌幅"],
                prev_close=row["昨收"],
                open_price=row["今开"],
                amount=row["收盘金额"],
                race_amount=row["抢筹成交金额"],
                race_ratio=row["抢筹占比"],
                race_pct=row["抢筹幅度"],
                board_days=row["天"],
                board_type=row["板"],
                created_at=datetime.now(),
            )
            records.append(record)
        
        return self._save_records(records)
    
    def _save_records(self, records: List[StockChipRace]) -> int:
        """
        内部方法：批量保存记录
        
        Args:
            records: 抢筹记录列表
            
        Returns:
            保存的记录数
        """
        try:
            session = self.db.get_session()
            
            for record in records:
                # 删除重复记录
                session.query(StockChipRace).filter(
                    StockChipRace.code == record.code,
                    StockChipRace.date == record.date,
                    StockChipRace.period == record.period
                ).delete()
            
            session.add_all(records)
            session.commit()
            
            count = len(records)
            logger.info(f"[ChipRaceRepository] 成功保存 {count} 条抢筹数据")
            return count
            
        except Exception as e:
            session.rollback()
            logger.error(f"[ChipRaceRepository] 保存抢筹数据失败: {e}")
            raise
        finally:
            session.close()
    
    def get_by_date(self, query_date: date, period: Optional[int] = None) -> List[StockChipRace]:
        """
        根据日期查询抢筹数据
        
        Args:
            query_date: 查询日期
            period: 周期类型，0=早盘，1=尾盘，None=全部
            
        Returns:
            抢筹数据列表
        """
        try:
            session = self.db.get_session()
            
            query = session.query(StockChipRace).filter(StockChipRace.date == query_date)
            if period is not None:
                query = query.filter(StockChipRace.period == period)
            
            results = query.all()
            session.close()
            
            return results
            
        except Exception as e:
            logger.error(f"[ChipRaceRepository] 查询抢筹数据失败: {e}")
            raise
    
    def fetch_and_save_open(self, query_date: Optional[date] = None) -> int:
        """
        获取并保存早盘抢筹数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            保存的记录数
        """
        date_str = query_date.strftime("%Y%m%d") if query_date else ""
        df = self.fetcher.get_chip_race_open(date_str)
        return self.save_chip_race_open(df, query_date)
    
    def fetch_and_save_close(self, query_date: Optional[date] = None) -> int:
        """
        获取并保存尾盘抢筹数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            保存的记录数
        """
        date_str = query_date.strftime("%Y%m%d") if query_date else ""
        df = self.fetcher.get_chip_race_close(date_str)
        return self.save_chip_race_close(df, query_date)
    
    def get_or_fetch_open(self, query_date: Optional[date] = None) -> List[StockChipRace]:
        """
        获取早盘抢筹数据，如果不存在则自动获取
        
        Args:
            query_date: 查询日期
            
        Returns:
            抢筹数据列表
        """
        query_date = query_date or date.today()
        
        # 先检查数据库
        results = self.get_by_date(query_date, period=0)
        
        if results:
            logger.debug(f"从数据库获取早盘抢筹数据: {query_date}, {len(results)} 条")
            return results
        
        # 数据库没有，从数据源获取
        logger.info(f"数据库未找到 {query_date} 的早盘抢筹数据，从数据源获取")
        self.fetch_and_save_open(query_date)
        # 返回获取的数据
        return self.get_by_date(query_date, period=0)
    
    def get_or_fetch_close(self, query_date: Optional[date] = None) -> List[StockChipRace]:
        """
        获取尾盘抢筹数据，如果不存在则自动获取
        
        Args:
            query_date: 查询日期
            
        Returns:
            抢筹数据列表
        """
        query_date = query_date or date.today()
        
        # 先检查数据库
        results = self.get_by_date(query_date, period=1)
        
        if results:
            logger.debug(f"从数据库获取尾盘抢筹数据: {query_date}, {len(results)} 条")
            return results
        
        # 数据库没有，从数据源获取
        logger.info(f"数据库未找到 {query_date} 的尾盘抢筹数据，从数据源获取")
        self.fetch_and_save_close(query_date)
        # 返回获取的数据
        return self.get_by_date(query_date, period=1)