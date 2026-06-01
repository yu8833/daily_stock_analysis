# -*- coding: utf-8 -*-
"""股票交易策略模块 / Stock Trading Strategies"""

from strategy.放量上涨.check import check_volume
from strategy.均线多头.check import check as keep_increasing_check
from strategy.停机坪.check import check as parking_apron_check
from strategy.回踩年线.check import check as backtrace_ma250_check
from strategy.突破平台.check import check as breakthrough_platform_check
from strategy.无大幅回撤.check import check as low_backtrace_increase_check
from strategy.海龟交易法则.check import check_enter as turtle_trade_check
from strategy.宽而窄的旗形.check import check_high_tight
from strategy.放量跌停.check import check as climax_limitdown_check
from strategy.低ATR成长.check import check_low_increase

__all__ = [
    "check_volume",
    "keep_increasing_check",
    "parking_apron_check",
    "backtrace_ma250_check",
    "breakthrough_platform_check",
    "low_backtrace_increase_check",
    "turtle_trade_check",
    "check_high_tight",
    "climax_limitdown_check",
    "check_low_increase",
]
