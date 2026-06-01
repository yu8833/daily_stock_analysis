# -*- coding: utf-8 -*-
"""停机坪策略 / Parking Apron Strategy

Rules:
1. 最近15日有涨幅大于9.5%，且必须是放量上涨
2. 紧接的下个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%
3. 接下2、3个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%，且每天涨跌幅在5%间
"""

from datetime import datetime

from strategy.海龟交易法则.check import check_enter as turtle_trade_check_enter


def check(code_name, data, date=None, threshold=15):
    """Check if stock meets parking apron criteria.

    Args:
        code_name: Tuple of (date, code) for the stock
        data: DataFrame with columns ['date', 'close', 'open', 'volume', 'p_change']
        date: Optional date to check against
        threshold: Lookback period (default 15)

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
        data = data.loc[mask]

    if len(data.index) < threshold:
        return False

    data = data.tail(n=threshold)

    limitup_row = [1000000, '']
    for _close, _p_change, _date in zip(data['close'].values, data['p_change'].values, data['date'].values):
        if _p_change > 9.5:
            if turtle_trade_check_enter(code_name, origin_data, date=datetime.date(datetime.strptime(_date, '%Y-%m-%d')), threshold=threshold):
                limitup_row[0] = _close
                limitup_row[1] = _date
                if check_internal(data, limitup_row):
                    return True
    return False


def check_internal(data, limitup_row):
    """Internal check for consolidation days after limit up.

    Args:
        data: DataFrame with stock data
        limitup_row: List containing [limitup_price, limitup_date]

    Returns:
        bool: True if consolidation criteria met
    """
    limitup_price = limitup_row[0]
    limitup_end = data.loc[(data['date'] > limitup_row[1])]
    limitup_end = limitup_end.head(n=3)

    if len(limitup_end.index) < 3:
        return False

    consolidation_day1 = limitup_end.iloc[0]
    consolidation_day23 = limitup_end.tail(n=2)

    if not (consolidation_day1['close'] > limitup_price and consolidation_day1['open'] > limitup_price and
            0.97 < consolidation_day1['close'] / consolidation_day1['open'] < 1.03):
        return False

    for _close, _p_change, _open in zip(consolidation_day23['close'].values, consolidation_day23['p_change'].values, consolidation_day23['open'].values):
        if not (0.97 < (_close / _open) < 1.03 and -5 < _p_change < 5
                and _close > limitup_price and _open > limitup_price):
            return False

    return True
