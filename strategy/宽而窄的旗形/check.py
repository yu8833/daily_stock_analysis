# -*- coding: utf-8 -*-
"""宽而窄的旗形策略 / High Tight Flag Strategy

Rules:
1. 必须至少上市交易60日
2. 当日收盘价/之前24~10日的最低价>=1.9
3. 之前24~10日必须连续两天涨幅大于等于9.5%
"""


def check_high_tight(code_name, data, date=None, threshold=60, istop=False):
    """Check if stock meets high tight flag criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change', 'high', 'low']
        date: Optional date to check against
        threshold: Lookback period (default 60)
        istop: Whether stock is on top list (龙虎榜) - required for this strategy

    Returns:
        bool: True if criteria met, False otherwise
    """
    if not istop:
        return False

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

    data = data.tail(n=24)
    data = data.head(n=14)

    low = data['low'].values.min()
    ratio_increase = data.iloc[-1]['high'] / low

    if ratio_increase < 1.9:
        return False

    previous_p_change = 0.0
    for _p_change in data['p_change'].values:
        if _p_change >= 9.5:
            if previous_p_change >= 9.5:
                return True
            else:
                previous_p_change = _p_change
        else:
            previous_p_change = 0.0

    return False
