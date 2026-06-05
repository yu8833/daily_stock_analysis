from data_provider.base import DataFetcherManager
from src.repositories.selection_repo import SelectionRepository
from src.repositories.stock_repo import StockRepository
from datetime import date, timedelta

manager = DataFetcherManager()
repo = SelectionRepository()
stock_repo = StockRepository()
query_date = date(2026, 6, 3)

selection_data = repo.get_by_date(query_date, use_cache=False)
print(f'共有 {len(selection_data)} 只股票，准备获取前100只的日线数据...')

success = 0
fail = 0
for i, stock in enumerate(selection_data[:100], 1):
    try:
        result = manager.get_daily_data(stock.code, days=200)
        df = result[0] if isinstance(result, tuple) else result
        
        if df is not None and hasattr(df, 'empty') and not df.empty:
            stock_repo.save_dataframe(df, stock.code)
            success += 1
            if i % 20 == 0:
                print(f'  已完成 {i}/100，成功 {success}，失败 {fail}')
        else:
            fail += 1
    except Exception as e:
        fail += 1
        if i % 20 == 0:
            print(f'  已完成 {i}/100，成功 {success}，失败 {fail}')

print(f'\n完成！成功获取 {success} 只，失败 {fail} 只')

# 验证数据
print('\n验证数据...')
has_60_days = 0
for stock in selection_data[:100]:
    daily_data = stock_repo.get_range(stock.code, query_date - timedelta(days=120), query_date)
    if daily_data and len(daily_data) >= 60:
        has_60_days += 1

print(f'前100只中现在有 {has_60_days} 只有60天以上数据')
