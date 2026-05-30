#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('/app/data/stock_analysis.db')
cursor = conn.cursor()

# 检查数据库中这些字段的实际值
cursor.execute('''
    SELECT directional_seo_1m, directional_seo_3m, directional_seo_6m, directional_seo_1y,
           recapitalize_1m, recapitalize_3m, recapitalize_6m, recapitalize_1y,
           equity_pledge_1m, equity_pledge_3m, equity_pledge_6m, equity_pledge_1y,
           high_recent_3days, high_recent_5days, high_recent_10days, high_recent_20days, high_recent_30days,
           low_recent_3days, low_recent_5days, low_recent_10days, low_recent_20days, low_recent_30days,
           win_market_3days, win_market_5days, win_market_10days, win_market_20days, win_market_30days
    FROM stock_selection 
    WHERE date = '2026-05-28'
    LIMIT 1
''')

row = cursor.fetchone()
print("数据库中第一条记录的原始值:")
print(f"directional_seo_1m: {repr(row[0])}, type={type(row[0])}")
print(f"directional_seo_3m: {repr(row[1])}, type={type(row[1])}")
print(f"directional_seo_6m: {repr(row[2])}, type={type(row[2])}")
print(f"directional_seo_1y: {repr(row[3])}, type={type(row[3])}")
print(f"recapitalize_1m: {repr(row[4])}, type={type(row[4])}")
print(f"recapitalize_3m: {repr(row[5])}, type={type(row[5])}")
print(f"recapitalize_6m: {repr(row[6])}, type={type(row[6])}")
print(f"recapitalize_1y: {repr(row[7])}, type={type(row[7])}")
print(f"equity_pledge_1m: {repr(row[8])}, type={type(row[8])}")
print(f"equity_pledge_3m: {repr(row[9])}, type={type(row[9])}")
print(f"equity_pledge_6m: {repr(row[10])}, type={type(row[10])}")
print(f"equity_pledge_1y: {repr(row[11])}, type={type(row[11])}")
print(f"high_recent_3days: {repr(row[12])}, type={type(row[12])}")
print(f"high_recent_5days: {repr(row[13])}, type={type(row[13])}")
print(f"high_recent_10days: {repr(row[14])}, type={type(row[14])}")
print(f"high_recent_20days: {repr(row[15])}, type={type(row[15])}")
print(f"high_recent_30days: {repr(row[16])}, type={type(row[16])}")
print(f"low_recent_3days: {repr(row[17])}, type={type(row[17])}")
print(f"low_recent_5days: {repr(row[18])}, type={type(row[18])}")
print(f"low_recent_10days: {repr(row[19])}, type={type(row[19])}")
print(f"low_recent_20days: {repr(row[20])}, type={type(row[20])}")
print(f"low_recent_30days: {repr(row[21])}, type={type(row[21])}")
print(f"win_market_3days: {repr(row[22])}, type={type(row[22])}")
print(f"win_market_5days: {repr(row[23])}, type={type(row[23])}")
print(f"win_market_10days: {repr(row[24])}, type={type(row[24])}")
print(f"win_market_20days: {repr(row[25])}, type={type(row[25])}")
print(f"win_market_30days: {repr(row[26])}, type={type(row[26])}")

conn.close()