# -*- coding: utf-8 -*-
"""突破平台策略 / Breakthrough Platform Strategy

Rules:
1. 60日内某日收盘价>=60日均线>开盘价
2. 且【1】放量上涨
3. 且【1】间之前时间，任意一天收盘价与60日均线偏离在-5%~20%之间。
"""

from datetime import datetime
import numpy as np
import talib as tl

from strategy.放量上涨.check import check_volume


def check(code_name, data, date=None, threshold=60):
    """Check if stock meets breakthrough platform criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change']
        date: Optional date to check against
        threshold: Lookback period (default 60)

    Returns:
        bool: True if criteria met, False otherwise
    """
    origin_data = data
    if date is None:
        end_date = code_name[0]
    else:
        end_date = date.strftime("%Y-%m-%d")

    if end_date is not None:
        mask = (data['date'] <= end_date)
        data = data.loc[mask].copy()

    if len(data.index) < threshold:
        return False

    data.loc[:, 'ma60'] = tl.MA(data['close'].values, timeperiod=60)
    data['ma60'].values[np.isnan(data['ma60'].values)] = 0.0

    data = data.tail(n=threshold)

    breakthrough_row = None
    for _close, _open, _date, _ma60 in zip(data['close'].values, data['open'].values, data['date'].values, data['ma60'].values):
        if _open < _ma60 <= _close:
            if check_volume(code_name, origin_data, date=datetime.date(datetime.strptime(_date, '%Y-%m-%d')), threshold=threshold):
                breakthrough_row = _date
                break

    if breakthrough_row is None:
        return False

    data_front = data.loc[(data['date'] < breakthrough_row) & (data['ma60'] > 0)]
    for _close, _ma60 in zip(data_front['close'].values, data_front['ma60'].values):
        if not (-0.05 < ((_ma60 - _close) / _ma60) < 0.2):
            return False

    return True
