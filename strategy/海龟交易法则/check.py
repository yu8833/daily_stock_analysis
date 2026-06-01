# -*- coding: utf-8 -*-
"""海龟交易法则策略 / Turtle Trading Strategy

Rules:
1. 当日收盘价 >= 最近60日最高收盘价
"""

BALANCE = 200000


def check_enter(code_name, data, date=None, threshold=60):
    """Check if stock meets turtle trading entry criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change']
        date: Optional date to check against
        threshold: Lookback period (default 60)

    Returns:
        bool: True if criteria met, False otherwise
    """
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask]

    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)

    max_price = 0
    for _close in data['close'].values:
        if _close > max_price:
            max_price = _close

    last_close = data.iloc[-1]['close']

    if last_close >= max_price:
        return True

    return False
