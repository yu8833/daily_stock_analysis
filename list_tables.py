#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('/app/data/stock_data.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 如果有 selection 相关的表，检查结构
for table in tables:
    if 'selection' in table[0].lower():
        print(f"\n表 {table[0]} 的结构:")
        cursor.execute(f"PRAGMA table_info({table[0]});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

conn.close()