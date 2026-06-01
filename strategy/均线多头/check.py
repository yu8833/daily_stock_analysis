# -*- coding: utf-8 -*-
"""均线多头策略 / Keep Increasing MA Strategy

持续上涨（MA30向上）
均线多头

Rules:
1. 30日前的30日均线 < 20日前的30日均线 < 10日前的30日均线 < 当日的30日均线
2. (当日的30日均线 / 30日前的30日均线) > 1.2
"""

import numpy as np
import talib as tl


def check(code_name, data, date=None, threshold=30):
    """Check if stock meets MA bull trend criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change']
        date: Optional date to check against
        threshold: Lookback period (default 30)

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

    data.loc[:, 'ma30'] = tl.MA(data['close'].values, timeperiod=30)
    data['ma30'].values[np.isnan(data['ma30'].values)] = 0.0

    data = data.tail(n=threshold)

    step1 = round(threshold / 3)
    step2 = round(threshold * 2 / 3)

    if (data.iloc[0]['ma30'] < data.iloc[step1]['ma30'] <
            data.iloc[step2]['ma30'] < data.iloc[-1]['ma30'] and
            data.iloc[-1]['ma30'] > 1.2 * data.iloc[0]['ma30']):
        return True
    else:
        return False
