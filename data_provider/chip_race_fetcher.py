# -*- coding: utf-8 -*-
"""
===================================
ChipRaceFetcher - 抢筹数据获取器
===================================

数据来源：通达信抢筹接口
特点：获取早盘抢筹和尾盘抢筹数据

接口说明：
- 早盘抢筹：period=0
- 尾盘抢筹：period=1
"""

import logging
import random
import time
from typing import Optional, Dict, Any, List

import pandas as pd
import requests

from .base import BaseFetcher, DataFetchError

logger = logging.getLogger(__name__)


class ChipRaceFetcher(BaseFetcher):
    """
    抢筹数据获取器
    
    获取通达信竞价抢筹数据，包括早盘抢筹和尾盘抢筹
    """
    
    name = "ChipRaceFetcher"
    priority = 10  # 较低优先级，作为补充数据源
    
    def __init__(self):
        self._base_url = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
        self._token = "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f"
        self._headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 TdxW",
        }
    
    def get_chip_race_open(self, date: str = "") -> pd.DataFrame:
        """
        获取早盘抢筹数据
        
        Args:
            date: 查询日期，格式 YYYYMMDD，为空则获取最新数据
            
        Returns:
            早盘抢筹数据 DataFrame
        """
        return self._fetch_chip_race(date, period=0)
    
    def get_chip_race_close(self, date: str = "") -> pd.DataFrame:
        """
        获取尾盘抢筹数据
        
        Args:
            date: 查询日期，格式 YYYYMMDD，为空则获取最新数据
            
        Returns:
            尾盘抢筹数据 DataFrame
        """
        return self._fetch_chip_race(date, period=1)
    
    def _fetch_chip_race(self, date: str, period: int) -> pd.DataFrame:
        """
        内部方法：获取抢筹数据
        
        Args:
            date: 查询日期
            period: 周期类型，0=早盘，1=尾盘
            
        Returns:
            抢筹数据 DataFrame
        """
        # sort: 1抢筹委托金额, 2抢筹成交金额, 3开盘金额, 4抢筹幅度, 5抢筹占比
        if date == "":
            params = [{
                "funcId": 20,
                "offset": 0,
                "count": 100,
                "sort": 1,
                "period": period,
                "Token": self._token,
                "modname": "JJQC"
            }]
        else:
            params = [{
                "funcId": 20,
                "offset": 0,
                "count": 100,
                "sort": 1,
                "period": period,
                "Token": self._token,
                "modname": "JJQC",
                "date": date
            }]
        
        # 随机休眠防封禁
        self.random_sleep(1.0, 2.0)
        
        try:
            logger.info(f"[ChipRaceFetcher] 获取抢筹数据: period={period}, date={date}")
            r = requests.post(
                self._base_url,
                json=params,
                headers=self._headers,
                timeout=30
            )
            r.raise_for_status()
            
            data_json = r.json()
            data = data_json.get("datas", [])
            
            if not data:
                logger.info("[ChipRaceFetcher] 未获取到抢筹数据")
                return pd.DataFrame()
            
            temp_df = pd.DataFrame(data)
            
            # 列名映射
            if period == 0:
                # 早盘抢筹
                temp_df.columns = [
                    "代码", "名称", "昨收", "今开", "开盘金额", "抢筹幅度",
                    "抢筹委托金额", "抢筹成交金额", "最新价", "_", "天", "板"
                ]
                amount_col = "开盘金额"
            else:
                # 尾盘抢筹
                temp_df.columns = [
                    "代码", "名称", "昨收", "今开", "收盘金额", "抢筹幅度",
                    "抢筹委托金额", "抢筹成交金额", "最新价", "_", "天", "板"
                ]
                amount_col = "收盘金额"
            
            # 数据处理
            temp_df["昨收"] = temp_df["昨收"] / 10000
            temp_df["今开"] = temp_df["今开"] / 10000
            temp_df["抢筹幅度"] = round(temp_df["抢筹幅度"] * 100, 2)
            temp_df["最新价"] = round(temp_df["最新价"], 2)
            temp_df["涨跌幅"] = round((temp_df["最新价"] / temp_df["昨收"] - 1) * 100, 2)
            temp_df["抢筹占比"] = round((temp_df["抢筹成交金额"] / temp_df[amount_col]) * 100, 2)
            
            # 选择输出列
            output_cols = [
                "代码", "名称", "最新价", "涨跌幅", "昨收", "今开",
                amount_col, "抢筹幅度", "抢筹委托金额", "抢筹成交金额", "抢筹占比", "天", "板"
            ]
            temp_df = temp_df[output_cols]
            
            logger.info(f"[ChipRaceFetcher] 获取成功: {len(temp_df)} 条数据")
            return temp_df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[ChipRaceFetcher] 获取抢筹数据失败: {e}")
            raise DataFetchError(f"抢筹数据获取失败: {e}") from e
    
    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        基类方法实现（未使用）
        """
        return pd.DataFrame()
    
    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """
        基类方法实现（未使用）
        """
        return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    fetcher = ChipRaceFetcher()
    
    print("=" * 50)
    print("测试早盘抢筹数据")
    print("=" * 50)
    try:
        df = fetcher.get_chip_race_open()
        print(f"获取成功，共 {len(df)} 条数据")
        print(df.head())
    except Exception as e:
        print(f"获取失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试尾盘抢筹数据")
    print("=" * 50)
    try:
        df = fetcher.get_chip_race_close()
        print(f"获取成功，共 {len(df)} 条数据")
        print(df.head())
    except Exception as e:
        print(f"获取失败: {e}")