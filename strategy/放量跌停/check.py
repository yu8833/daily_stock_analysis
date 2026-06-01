# -*- coding: utf-8 -*-
"""放量跌停策略 / Climax Limitdown Strategy

Rules:
1. 跌幅>9.5%
2. 成交额不低于2亿
3. 成交量至少是5日平均成交量的4倍
"""

import numpy as np
import talib as tl


def check(code_name, data, date=None, threshold=60):
    """Check if stock meets climax limitdown criteria.

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
        data = data.loc[mask].copy()

    if len(data.index) < threshold:
        return False

    p_change = data.iloc[-1]['p_change']
    if p_change > -9.5:
        return False

    data.loc[:, 'vol_ma5'] = tl.MA(data['volume'].values, timeperiod=5)
    data['vol_ma5'].values[np.isnan(data['vol_ma5'].values)] = 0.0

    data = data.tail(n=threshold + 1)
    if len(data.index) < threshold + 1:
        return False

    last_close = data.iloc[-1]['close']
    last_vol = data.iloc[-1]['volume']

    amount = last_close * last_vol

    if amount < 200000000:
        return False

    data = data.head(n=threshold)

    mean_vol = data.iloc[-1]['vol_ma5']

    vol_ratio = last_vol / mean_vol
    if vol_ratio >= 4:
        return True
    else:
        return False
