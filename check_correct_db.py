#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('/app/data/stock_analysis.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查 selection 相关的表
for table in tables:
    if 'selection' in table[0].lower():
        print(f"\n表 {table[0]} 的结构:")
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        # 检查数据
        print(f"\n表 {table[0]} 的数据行数:")
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"  总行数: {count}")
        
        cursor.execute(f"SELECT DISTINCT date FROM {table[0]} ORDER BY date DESC LIMIT 5;")
        dates = cursor.fetchall()
        print(f"  最近5个日期: {[d[0] for d in dates]}")

conn.close()