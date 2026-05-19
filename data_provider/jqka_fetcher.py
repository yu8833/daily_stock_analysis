# -*- coding: utf-8 -*-
"""
===================================
同花顺数据获取器
===================================

职责：
1. 获取涨停原因数据
2. 获取涨停详细原因
"""

import logging
from typing import Optional, List, Dict, Any
import pandas as pd
import requests
import re
import numpy as np

from data_provider.base import BaseFetcher

logger = logging.getLogger(__name__)


class TenJqkaFetcher(BaseFetcher):
    """同花顺数据获取器"""
    
    name = "10jqka"
    priority = 2  # 优先级高于 pytdx 和 baostock
    
    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Thx"
        })
    
    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """实现抽象方法 - 获取原始数据（本数据源不支持）"""
        return pd.DataFrame()
    
    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """实现抽象方法 - 标准化数据（本数据源不支持）"""
        return df
    
    def get_limit_up_reason(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取同花顺涨停原因数据
        
        Args:
            date: 日期（YYYY-MM-DD）
            
        Returns:
            涨停股票列表，包含代码、名称、原因、详因、换手率、成交量、成交额等
        """
        url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date}/orderby/date/orderway/desc/charset/GBK/"
        
        try:
            logger.info(f"[10jqka] 获取涨停原因数据: {date}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'http://zx.10jqka.com.cn/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            response = self._session.get(url, headers=headers, timeout=30)
            response.encoding = 'UTF-8'
            data_json = response.json()
            
            data = data_json.get("data", [])
            if not data:
                logger.info(f"[10jqka] 未获取到 {date} 的涨停数据")
                return []
            
            temp_df = pd.DataFrame(data)
            
            # 动态字段映射：API 返回的字段名可能不同
            # 历史数据字段: id, name, code, reason, date, close, zhangdie, zhangfu, huanshou, chengjiaoe, chengjiaoliang, ddejingliang, market
            # 盘中数据字段: id, name, code, reason, date, market
            
            # 标准化字段名称
            field_mapping = {
                'id': 'ID',
                'name': '名称',
                'code': '代码',
                'reason': '原因',
                'date': '日期',
                'close': '最新价',
                'zhangdie': '涨跌额',
                'zhangfu': '涨跌幅',
                'huanshou': '换手率',
                'chengjiaoe': '成交额',
                'chengjiaoliang': '成交量',
                'ddejingliang': 'DDE',
            }
            
            # 重命名已知字段
            temp_df = temp_df.rename(columns=lambda x: field_mapping.get(x, x))
            
            # 确保必要字段存在
            for col in ["ID", "名称", "代码", "原因", "日期", "最新价", "涨跌额", "涨跌幅", "换手率", "成交额", "成交量", "DDE"]:
                if col not in temp_df.columns:
                    temp_df[col] = np.nan
            
            # 获取详细原因
            temp_df["详因"] = temp_df.apply(self._get_limitup_detail, axis=1)
            
            # 处理换手率（保留两位小数）
            temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors='coerce').round(2)
            
            # 选择需要的列
            result_df = temp_df[[
                "日期",
                "代码",
                "名称",
                "原因",
                "详因",
                "最新价",
                "涨跌幅",
                "涨跌额",
                "换手率",
                "成交量",
                "成交额",
                "DDE",
            ]]
            
            return result_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"[10jqka] 获取涨停原因失败: {e}", exc_info=True)
            return None
    
    def _get_limitup_detail(self, row) -> str:
        """
        获取涨停详细原因
        
        Args:
            row: 包含ID的行数据
            
        Returns:
            详细原因字符串
        """
        try:
            row_id = row.get('ID')
            if not row_id:
                return ""
                
            url = f"http://zx.10jqka.com.cn/event/harden/stockreason/id/{row_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, image/apng, */*;q=0.8',
                'Referer': 'http://zx.10jqka.com.cn/',
            }
            
            response = self._session.get(url, headers=headers, timeout=15)
            response.encoding = 'UTF-8'
            data_text = response.text
            
            # 提取详细原因 - 数据是纯文本格式，不是 Unicode 转义
            pattern_data = re.search(r"var data = '(.*?)';", data_text)
            if pattern_data:
                detail = pattern_data.group(1)
                
                # 清理HTML实体
                detail = detail.replace("&lt;spanclass=&quot;hl&quot;&gt;", "") \
                              .replace("&lt;/span&gt;", "") \
                              .replace("&amp;quot;", "\"") \
                              .replace("&lt;p&gt;", "") \
                              .replace("&lt;/p&gt;", "") \
                              .replace("<p>", "") \
                              .replace("</p>", "")
                
                return detail.strip()
            
            return ""
        except Exception as e:
            logger.debug(f"[10jqka] 获取涨停详因失败 (ID={row.get('ID')}): {e}")
            return ""
    
    def get_limit_up_pool(
        self,
        date: Optional[str] = None,
        n: int = 20,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        获取涨停池数据（实现基类接口）
        
        Args:
            date: 日期（YYYYMMDD），默认当天
            n: 返回条数
            
        Returns:
            涨停股票列表
        """
        import datetime
        
        query_date = date
        if not query_date:
            query_date = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            # 转换格式 YYYYMMDD -> YYYY-MM-DD
            if len(query_date) == 8:
                query_date = f"{query_date[:4]}-{query_date[4:6]}-{query_date[6:]}"
        
        result = self.get_limit_up_reason(query_date)
        if result:
            # 转换字段名称以匹配现有接口
            formatted_result = []
            for item in result[:n]:
                formatted_result.append({
                    'code': str(item.get('代码', '')).strip(),
                    'name': str(item.get('名称', '')).strip(),
                    'reason': str(item.get('原因', '')).strip(),
                    'detail_reason': str(item.get('详因', '')).strip(),
                    'turnover_rate': item.get('换手率'),
                    'volume': item.get('成交量'),
                    'amount': item.get('成交额'),
                    'change_pct': item.get('涨跌幅'),
                    'price': item.get('最新价'),
                    'industry': None,
                    'first_limit_time': None,
                    'last_limit_time': None,
                    'break_count': None,
                    'seal_amount': None,
                    'limit_stat': str(item.get('原因', '')).strip(),
                    'consecutive_boards': None,
                })
            return formatted_result
        
        return None
