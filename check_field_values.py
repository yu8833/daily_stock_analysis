#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('/app/data/stock_analysis.db')
cursor = conn.cursor()

# 检查2026-05-28的字段值
cursor.execute('''
    SELECT directional_seo_6m, directional_seo_1y, 
           recapitalize_1m, recapitalize_3m, recapitalize_6m, recapitalize_1y,
           equity_pledge_1m, equity_pledge_3m, equity_pledge_6m, equity_pledge_1y,
           high_recent_3days, high_recent_5days, high_recent_10days, high_recent_20days, high_recent_30days,
           low_recent_3days, low_recent_5days, low_recent_10days, low_recent_20days, low_recent_30days,
           win_market_3days, win_market_5days, win_market_10days, win_market_20days, win_market_30days
    FROM stock_selection 
    WHERE date = '2026-05-28'
    LIMIT 5
''')

rows = cursor.fetchall()
print("数据库中2026-05-28的前5条记录：")
for i, row in enumerate(rows):
    print(f"\n第{i+1}条:")
    print(f"  定增近6月: {repr(row[0])}, 定增近1年: {repr(row[1])}")
    print(f"  重组近1月: {repr(row[2])}, 重组近3月: {repr(row[3])}, 重组近6月: {repr(row[4])}, 重组近1年: {repr(row[5])}")
    print(f"  质押近1月: {repr(row[6])}, 质押近3月: {repr(row[7])}, 质押近6月: {repr(row[8])}, 质押近1年: {repr(row[9])}")
    print(f"  近期新高近3日: {repr(row[10])}, 近5日: {repr(row[11])}, 近10日: {repr(row[12])}, 近20日: {repr(row[13])}, 近30日: {repr(row[14])}")
    print(f"  近期新低近3日: {repr(row[15])}, 近5日: {repr(row[16])}, 近10日: {repr(row[17])}, 近20日: {repr(row[18])}, 近30日: {repr(row[19])}")
    print(f"  跑赢大盘近3日: {repr(row[20])}, 近5日: {repr(row[21])}, 近10日: {repr(row[22])}, 近20日: {repr(row[23])}, 近30日: {repr(row[24])}")

# 统计这些字段的非空值数量
print("\n\n字段统计（2026-05-28）:")
fields = [
    'directional_seo_6m', 'directional_seo_1y',
    'recapitalize_1m', 'recapitalize_3m', 'recapitalize_6m', 'recapitalize_1y',
    'equity_pledge_1m', 'equity_pledge_3m', 'equity_pledge_6m', 'equity_pledge_1y',
    'high_recent_3days', 'high_recent_5days', 'high_recent_10days', 'high_recent_20days', 'high_recent_30days',
    'low_recent_3days', 'low_recent_5days', 'low_recent_10days', 'low_recent_20days', 'low_recent_30days',
    'win_market_3days', 'win_market_5days', 'win_market_10days', 'win_market_20days', 'win_market_30days',
]
for field in fields:
    cursor.execute(f"SELECT COUNT(*) FROM stock_selection WHERE date = '2026-05-28' AND {field} IS NOT NULL AND {field} != '';")
    count = cursor.fetchone()[0]
    cursor.execute(f"SELECT COUNT(*) FROM stock_selection WHERE date = '2026-05-28';")
    total = cursor.fetchone()[0]
    print(f"  {field}: 非空={count}/{total}")

conn.close()