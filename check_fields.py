#!/usr/bin/env python
"""
检查新增字段的数据情况
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import get_session, StockSelection
from datetime import datetime

with get_session() as session:
    today = datetime.now().date()
    query = session.query(StockSelection).filter(StockSelection.trade_date == today)
    
    total = query.count()
    print(f'Total stocks: {total}')
    
    # 检查每个字段
    has_is_issue_break = query.filter(StockSelection.is_issue_break.isnot(None)).count()
    has_is_bps_break = query.filter(StockSelection.is_bps_break.isnot(None)).count()
    has_now_newhigh = query.filter(StockSelection.now_newhigh.isnot(None)).count()
    has_now_newlow = query.filter(StockSelection.now_newlow.isnot(None)).count()
    has_mutual_netbuy = query.filter(StockSelection.mutual_netbuy_amt.isnot(None)).count()
    has_par_dividend = query.filter(StockSelection.par_dividend.isnot(None)).count()
    has_predict_type = query.filter(StockSelection.predict_type.isnot(None)).count()
    
    print(f'破发 (有数据): {has_is_issue_break}')
    print(f'破净 (有数据): {has_is_bps_break}')
    print(f'今日历史新高 (有数据): {has_now_newhigh}')
    print(f'今日历史新低 (有数据): {has_now_newlow}')
    print(f'沪深股通净买入 (有数据): {has_mutual_netbuy}')
    print(f'每股红股 (有数据): {has_par_dividend}')
    print(f'业绩预告 (有数据): {has_predict_type}')
    print()
    
    # 打印几个样本
    print("样本数据:")
    samples = query.limit(3).all()
    for s in samples:
        print(f"  {s.code} {s.name}:")
        print(f"    破发: {s.is_issue_break}")
        print(f"    破净: {s.is_bps_break}")
        print(f"    今日新高: {s.now_newhigh}")
        print(f"    今日新低: {s.now_newlow}")
