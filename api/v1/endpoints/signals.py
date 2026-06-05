# -*- coding: utf-8 -*-
"""
===================================
交易信号接口
===================================

职责：
1. GET /api/v1/signals/buy 获取买入信号
2. GET /api/v1/signals/sell 获取卖出信号
3. 基于均线三买三卖系统计算买卖信号
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query

from src.repositories.selection_repo import SelectionRepository
from src.repositories.stock_repo import StockRepository
from src.storage import DatabaseManager, StockDaily
from sqlalchemy import select, and_
from data_provider import DataFetcherManager

logger = logging.getLogger(__name__)

router = APIRouter()


def calculate_ma(prices: List[float], period: int) -> Optional[float]:
    """
    计算移动平均线
    """
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_bias(current_price: float, ma: float) -> float:
    """
    计算BIAS指标
    """
    if ma == 0:
        return 0
    return ((current_price - ma) / ma) * 100


def get_daily_data(stock_code: str, query_date: date, days: int = 120) -> List[StockDaily]:
    """
    获取股票日线数据，仅从数据库获取，不进行网络请求
    """
    repo = StockRepository()
    start_date = query_date - timedelta(days=days)
    
    # 仅从数据库获取，不进行网络请求
    db_data = repo.get_range(stock_code, start_date, query_date)
    
    return db_data


def check_buy_signals(stock_code: str, stock_name: str, query_date: date) -> List[dict]:
    """
    检查买入信号
    
    三买三卖系统买入规则：
    - B1 - 第一类买点：BIAS跌至-25%左右，小仓位试探（目标仓位1/3）
    - B2 - 第二类买点：放量中阳突破MA60，标准建仓（目标仓位2/3）
    - B3 - 第三类买点：回调至MA60附近，加至满仓
    """
    signals = []

    results = get_daily_data(stock_code, query_date, days=120)

    if len(results) < 60:
        return signals

    closes = [float(r.close) for r in results if r.close]
    opens = [float(r.open) for r in results if r.open]
    volumes = [float(r.volume) for r in results if r.volume]

    if len(closes) < 60 or len(opens) < 60 or len(volumes) < 60:
        return signals

    ma5 = calculate_ma(closes, 5)
    ma8 = calculate_ma(closes, 8)
    ma13 = calculate_ma(closes, 13)
    ma55 = calculate_ma(closes, 55)
    ma60 = calculate_ma(closes, 60)

    if ma55 is None or ma60 is None:
        return signals

    current_price = closes[-1]
    current_open = opens[-1]
    current_volume = volumes[-1]

    bias60 = calculate_bias(current_price, ma60)

    avg_volume_20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else current_volume
    volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
    
    body_change = ((current_price - current_open) / current_open) * 100 if current_open != 0 else 0

    # B1 - 第一类买点：BIAS跌至-20%至-30%区间，小仓位试探
    if -30 <= bias60 <= -20:
        signals.append({
            "code": stock_code,
            "name": stock_name,
            "stock_code": stock_code,
            "stock_name": stock_name,
            "signal_type": "buy",
            "signal_name": "B1 - 第一类买点",
            "score": 7,
            "recommendation": "小仓位试探 (目标仓位1/3)",
            "date": query_date.isoformat(),
            "bias60": round(bias60, 2)
        })

    # B2 - 第二类买点：放量中阳突破MA55和MA60，标准建仓
    # 条件：放量(>1.5倍20日均量) + 中阳线(实体涨幅>=5%) + 收盘价同时站上MA55和MA60
    ma_break = current_price > ma55 and current_price > ma60
    if ma_break and volume_ratio > 1.5 and body_change >= 5:
        signals.append({
            "code": stock_code,
            "name": stock_name,
            "stock_code": stock_code,
            "stock_name": stock_name,
            "signal_type": "buy",
            "signal_name": "B2 - 第二类买点",
            "score": 8,
            "recommendation": "标准建仓 (目标仓位2/3)",
            "date": query_date.isoformat(),
            "volume_ratio": round(volume_ratio, 2),
            "body_change": round(body_change, 2)
        })

    # B3 - 第三类买点：回调至MA60附近，加至满仓
    # 条件：近30日内曾有较大正乖离 + MA13>MA55（中期趋势未破坏）且BIAS在[-5, 5]区间且放量中阳
    # 前提：近30日内BIAS最高值> +15%，说明之前有过一波上涨
    recent_biases = []
    for i in range(min(30, len(closes)-1)):
        idx = len(closes) - 1 - i
        if idx >= 59:
            ma60_val = sum(closes[idx-59:idx+1]) / 60
            recent_biases.append(((closes[idx] - ma60_val) / ma60_val) * 100)
    max_recent_bias = max(recent_biases) if recent_biases else 0
    
    has_recent_rally = max_recent_bias > 15
    
    if has_recent_rally and ma13 and ma13 > ma55 and -5 <= bias60 <= 5 and volume_ratio > 1.2 and body_change >= 3:
        signals.append({
            "code": stock_code,
            "name": stock_name,
            "stock_code": stock_code,
            "stock_name": stock_name,
            "signal_type": "buy",
            "signal_name": "B3 - 第三类买点",
            "score": 9,
            "recommendation": "加至满仓",
            "date": query_date.isoformat(),
            "bias60": round(bias60, 2)
        })

    return signals


def check_buy_signals_for_sell_filter(stock_code: str, query_date: date, days_lookback: int = 60) -> bool:
    """
    检查近期是否有买入信号（用于过滤卖出信号）
    """
    results = get_daily_data(stock_code, query_date, days=days_lookback + 60)
    
    if len(results) < 60:
        return False
    
    closes = [float(r.close) for r in results if r.close]
    
    for i in range(min(days_lookback, len(closes) - 60)):
        idx = len(closes) - 60 - i
        if idx < 0:
            continue
        
        current_closes = closes[:idx + 60]
        current_price = current_closes[-1]
        
        ma60 = sum(current_closes[-60:]) / 60
        bias60 = ((current_price - ma60) / ma60) * 100
        
        # 检查是否有B1买入信号
        if -30 <= bias60 <= -20:
            return True
        
        # 检查是否有B2买入信号（简化检查）
        ma55 = sum(current_closes[-55:]) / 55 if len(current_closes) >= 55 else None
        if ma55 and current_price > ma55 and current_price > ma60:
            return True
    
    return False


def check_sell_signals(stock_code: str, stock_name: str, query_date: date) -> List[dict]:
    """
    检查卖出信号
    
    三买三卖系统卖出规则：
    - S1 - 第一类卖点：BIAS达到+30%以上，部分止盈（卖出1/3）
    - S2 - 第二类卖点：收盘价连续2天低于MA5、MA8和MA13，加大止盈（仅留1/3）
    - S3 - 第三类卖点：收盘价跌破MA55和MA60，且MA60斜率转为负值，全部清仓
    
    重要：卖出信号只针对近期（60天内）有过买入信号的股票
    """
    signals = []

    # 检查近期是否有买入信号，没有则直接返回空
    if not check_buy_signals_for_sell_filter(stock_code, query_date):
        return signals

    results = get_daily_data(stock_code, query_date, days=120)

    if len(results) < 60:
        return signals

    closes = [float(r.close) for r in results if r.close]

    if len(closes) < 60:
        return signals

    ma5 = calculate_ma(closes, 5)
    ma8 = calculate_ma(closes, 8)
    ma13 = calculate_ma(closes, 13)
    ma55 = calculate_ma(closes, 55)
    ma60 = calculate_ma(closes, 60)

    if ma55 is None or ma60 is None:
        return signals

    current_price = closes[-1]
    bias60 = calculate_bias(current_price, ma60)

    # S1 - 第一类卖点：BIAS达到+30%以上，部分止盈
    if bias60 >= 30:
        signals.append({
            "code": stock_code,
            "name": stock_name,
            "stock_code": stock_code,
            "stock_name": stock_name,
            "signal_type": "sell",
            "signal_name": "S1 - 第一类卖点",
            "score": 8,
            "recommendation": "部分止盈 (卖出1/3)",
            "date": query_date.isoformat(),
            "bias60": round(bias60, 2)
        })

    # S2 - 第二类卖点：收盘价连续2天全部跌破短期均线组(MA5/MA8/MA13)，加大止盈
    # 额外条件：当前价格低于MA60 + 短期均线空头排列(MA5 < MA13)
    if ma5 and ma8 and ma13 and ma60 and len(closes) >= 2:
        # 获取最近两天的收盘价
        yesterday_close = closes[-2]
        # 检查是否连续2天收盘价都低于所有短期均线
        today_below_all = current_price < ma5 and current_price < ma8 and current_price < ma13
        yesterday_below_all = yesterday_close < ma5 and yesterday_close < ma8 and yesterday_close < ma13
        # 增加条件：当前价格低于MA60，确保中期趋势也向下
        below_ma60 = current_price < ma60
        # 增加条件：短期均线空头排列(MA5 < MA13)
        short_term_bearish = ma5 < ma13
        if today_below_all and yesterday_below_all and below_ma60 and short_term_bearish:
            signals.append({
                "code": stock_code,
                "name": stock_name,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "signal_type": "sell",
                "signal_name": "S2 - 第二类卖点",
                "score": 9,
                "recommendation": "加大止盈 (仅留1/3)",
                "date": query_date.isoformat()
            })

    # S3 - 第三类卖点：收盘价跌破MA55和MA60，且MA60斜率转为负值，全部清仓
    if ma55 and ma60:
        below_mas = current_price < ma55 and current_price < ma60
        
        # 检查MA60是否拐头向下：比较5天前的MA60与当前MA60
        ma60_slope_negative = False
        if len(closes) >= 70:
            ma60_5_days_ago = calculate_ma(closes[:-5], 60)
            if ma60_5_days_ago and ma60_5_days_ago > ma60:
                ma60_slope_negative = True
        
        if below_mas and ma60_slope_negative:
            signals.append({
                "code": stock_code,
                "name": stock_name,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "signal_type": "sell",
                "signal_name": "S3 - 第三类卖点",
                "score": 10,
                "recommendation": "全部清仓",
                "date": query_date.isoformat()
            })

    return signals


@router.get("/buy", tags=["Signals"])
def get_buy_signals(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    获取买入信号
    
    三买三卖系统买入规则：
    - B1 - 第一类买点：BIAS跌至-25%左右，小仓位试探（目标仓位1/3）
    - B2 - 第二类买点：放量中阳突破MA60，标准建仓（目标仓位2/3）
    - B3 - 第三类买点：回调至MA60附近，加至满仓
    """
    try:
        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = datetime.now().date()

        repo = SelectionRepository()
        selection_data = repo.get_by_date(query_date, use_cache=False)

        if not selection_data:
            return []

        all_signals = []

        for stock in selection_data:
            try:
                signals = check_buy_signals(stock.code, stock.name, query_date)

                for signal in signals:
                    signal.update({
                        "new_price": float(stock.new_price) if stock.new_price else None,
                        "change_rate": float(stock.change_rate) if stock.change_rate else None,
                        "volume_ratio": float(stock.volume_ratio) if stock.volume_ratio else None,
                        "pe": float(stock.pe) if stock.pe else None,
                        "pbnewmrq": float(stock.pbnewmrq) if stock.pbnewmrq else None,
                        "roe_weight": float(stock.roe_weight) if stock.roe_weight else None,
                        "sale_gpr": float(stock.sale_gpr) if stock.sale_gpr else None,
                        "netprofit_yoy_ratio": float(stock.netprofit_yoy_ratio) if stock.netprofit_yoy_ratio else None,
                    })
                    all_signals.append(signal)
            except Exception as e:
                logger.debug(f"处理股票 {stock.code} 失败: {e}")

        all_signals.sort(key=lambda x: x['score'], reverse=True)

        return all_signals

    except Exception as e:
        logger.error(f"获取买入信号失败: {e}")
        raise HTTPException(status_code=500, detail="获取买入信号失败")


@router.get("/sell", tags=["Signals"])
def get_sell_signals(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    获取卖出信号
    
    三买三卖系统卖出规则：
    - S1 - 第一类卖点：BIAS达到+30%以上，部分止盈（卖出1/3）
    - S2 - 第二类卖点：跌破短期均线组，加大止盈（仅留1/3）
    - S3 - 第三类卖点：跌破中期均线组+MA60拐头向下，全部清仓
    """
    try:
        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = datetime.now().date()

        repo = SelectionRepository()
        selection_data = repo.get_by_date(query_date, use_cache=False)

        if not selection_data:
            return []

        all_signals = []

        for stock in selection_data:
            try:
                signals = check_sell_signals(stock.code, stock.name, query_date)

                for signal in signals:
                    signal.update({
                        "new_price": float(stock.new_price) if stock.new_price else None,
                        "change_rate": float(stock.change_rate) if stock.change_rate else None,
                        "volume_ratio": float(stock.volume_ratio) if stock.volume_ratio else None,
                        "pe": float(stock.pe) if stock.pe else None,
                        "pbnewmrq": float(stock.pbnewmrq) if stock.pbnewmrq else None,
                        "roe_weight": float(stock.roe_weight) if stock.roe_weight else None,
                        "sale_gpr": float(stock.sale_gpr) if stock.sale_gpr else None,
                        "netprofit_yoy_ratio": float(stock.netprofit_yoy_ratio) if stock.netprofit_yoy_ratio else None,
                    })
                    all_signals.append(signal)
            except Exception as e:
                logger.debug(f"处理股票 {stock.code} 失败: {e}")

        all_signals.sort(key=lambda x: x['score'], reverse=True)

        return all_signals

    except Exception as e:
        logger.error(f"获取卖出信号失败: {e}")
        raise HTTPException(status_code=500, detail="获取卖出信号失败")