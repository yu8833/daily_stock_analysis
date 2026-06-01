# -*- coding: utf-8 -*-
"""低ATR成长策略 / Low ATR Growth Strategy

Rules:
1. 必须至少上市交易250日
2. 最近10个交易日的最高收盘价必须比最近10个交易日的最低收盘价高1.1倍
"""


def check_low_increase(code_name, data, date=None, ma_short=30, ma_long=250, threshold=10):
    """Check if stock meets low ATR growth criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change']
        date: Optional date to check against
        ma_short: Short MA period (default 30)
        ma_long: Long MA period (default 250)
        threshold: Lookback period for highs/lows (default 10)

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

    if len(data.index) < ma_long:
        return False

    data = data.tail(n=threshold)
    inc_days = 0
    dec_days = 0
    days_count = len(data.index)

    if days_count < threshold:
        return False

    lowest_row = 1000000
    highest_row = 0

    total_change = 0.0
    for _close, _p_change in zip(data['close'].values, data['p_change'].values):
        if _p_change > 0:
            total_change += abs(_p_change)
            inc_days = inc_days + 1
        elif _p_change < 0:
            total_change += abs(_p_change)
            dec_days = dec_days + 1

        if _close > highest_row:
            highest_row = _close
        elif _close < lowest_row:
            lowest_row = _close

    atr = total_change / days_count
    if atr > 10:
        return False

    ratio = (highest_row - lowest_row) / lowest_row

    if ratio > 1.1:
        return True

    return False
