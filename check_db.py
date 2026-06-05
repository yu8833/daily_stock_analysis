#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库中的抢筹数据"""

import sqlite3
import sys
from datetime import datetime

DB_PATH = 'data/stock_analysis.db'

def check_chip_race_data():
    """检查抢筹数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("检查数据库中的抢筹数据")
        print("=" * 80)
        
        # 1. 查看表结构
        print("\n[1] 表结构:")
        cursor.execute("PRAGMA table_info(stock_chip_race)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 2. 按日期分组统计
        print("\n[2] 按日期分组统计:")
        cursor.execute("""
            SELECT date, period, COUNT(*) as count, 
                   MIN(created_at) as first_create,
                   MAX(created_at) as last_create
            FROM stock_chip_race 
            GROUP BY date, period
            ORDER BY date DESC, period
        """)
        rows = cursor.fetchall()
        print(f"  {'日期':<12} {'类型':<10} {'数量':<8} {'首次创建':<20} {'最后更新':<20}")
        print("  " + "-" * 75)
        for row in rows:
            period_name = "早盘" if row[1] == 0 else "尾盘"
            print(f"  {row[0]:<12} {period_name:<10} {row[2]:<8} {row[3]:<20} {row[4]:<20}")
        
        # 3. 查看2026-05-26的详细数据
        print("\n[3] 2026-05-26 的详细数据:")
        cursor.execute("""
            SELECT date, period, code, name, latest_price, change_pct,
                   race_amount, race_ratio, race_pct
            FROM stock_chip_race 
            WHERE date = '2026-05-26'
            ORDER BY period, change_pct DESC
            LIMIT 5
        """)
        rows = cursor.fetchall()
        print(f"  {'日期':<12} {'类型':<8} {'代码':<10} {'名称':<15} {'最新价':<10} {'涨跌幅':<10} {'抢筹金额':<15}")
        print("  " + "-" * 85)
        for row in rows:
            period_name = "早盘" if row[1] == 0 else "尾盘"
            print(f"  {row[0]:<12} {period_name:<8} {row[2]:<10} {row[3]:<15} {row[4]:<10.2f} {row[5]:<10.2f} {row[6]:<15.2f}")
        
        # 4. 统计各日期的总数
        print("\n[4] 各日期数据统计:")
        cursor.execute("""
            SELECT date, COUNT(*) as total
            FROM stock_chip_race 
            GROUP BY date
            ORDER BY date DESC
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"  {row[0]}: {row[1]} 条")
        
        conn.close()
        print("\n" + "=" * 80)
        print("检查完成！")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_chip_race_data()
    sys.exit(0 if success else 1)
