# -*- coding: utf-8 -*-
"""
===================================
买入卖出信号接口
===================================

职责：
1. GET /api/v1/buy 获取买入信号股票
2. GET /api/v1/sell 获取卖出信号股票
3. 基于技术指标筛选股票
4. 生成交易理由
"""

import logging
import re
from datetime import date as DateType, datetime
from typing import Optional, Dict, List

from fastapi import APIRouter, HTTPException, Query

from api.v1.schemas.common import ErrorResponse
from src.repositories.selection_repo import SelectionRepository

logger = logging.getLogger(__name__)

router = APIRouter()
sell_router = APIRouter()


def is_trading_day(check_date: DateType) -> bool:
    """
    检查是否为交易日（中国A股）

    Args:
        check_date: 要检查的日期

    Returns:
        是否为交易日（周一到周五且非节假日返回True，周六周日或节假日返回False）
    """
    if check_date.weekday() >= 5:
        return False

    month = check_date.month
    day = check_date.day

    holidays_2026 = [
        (1, 1),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
        (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
        (4, 4), (4, 5), (4, 6),
        (6, 19), (6, 20), (6, 21),
        (9, 25), (9, 26), (9, 27),
    ]

    return (month, day) not in holidays_2026


def _is_st_stock(name: str) -> bool:
    """检查是否为ST股票（*ST、ST、退）"""
    if not name:
        return False
    name_upper = name.upper()
    return '*ST' in name_upper or 'ST' in name_upper or '退' in name


def _regex_match(text: str, pattern: str) -> bool:
    """
    使用正则表达式匹配文本
    
    Args:
        text: 待匹配的文本
        pattern: 正则表达式模式（不区分大小写）
    
    Returns:
        是否匹配成功
    """
    if not text or not pattern:
        return False
    try:
        return bool(re.search(pattern, text, re.IGNORECASE))
    except re.error:
        return pattern.lower() in text.lower()


def _generate_buy_reason(item) -> str:
    """生成买入理由"""
    reasons = []

    # MACD金叉
    if getattr(item, 'macd_golden_fork', None) == '1':
        reasons.append("MACD金叉")

    # KDJ金叉
    if getattr(item, 'kdj_golden_fork', None) == '1':
        reasons.append("KDJ金叉")

    # 放量突破
    if getattr(item, 'break_through', None) == '1':
        reasons.append("放量突破")

    # 均线多头排列
    if getattr(item, 'long_avg_array', None) == '1':
        reasons.append("均线多头排列")

    # 低位资金净流入
    if getattr(item, 'low_funds_inflow', None) == '1':
        reasons.append("低位资金净流入")

    # 向上突破均线
    if getattr(item, 'breakup_ma_5days', None) == '1':
        reasons.append("突破5日均线")
    elif getattr(item, 'breakup_ma_10days', None) == '1':
        reasons.append("突破10日均线")

    # K线形态买入信号
    if getattr(item, 'one_dayang_line', None) == '1':
        reasons.append("大阳线")
    elif getattr(item, 'two_dayang_lines', None) == '1':
        reasons.append("两阳夹一阴")
    elif getattr(item, 'rise_sun', None) == '1':
        reasons.append("旭日东升")
    elif getattr(item, 'power_fulgun', None) == '1':
        reasons.append("多方炮")
    elif getattr(item, 'morning_star', None) == '1':
        reasons.append("早晨之星")
    elif getattr(item, 'first_dawn', None) == '1':
        reasons.append("曙光初现")
    elif getattr(item, 'reversing_hammer', None) == '1':
        reasons.append("倒锤头")

    # 趋势位置分析
    try:
        if item.change_rate and float(item.change_rate) > 5:
            reasons.append("强势上涨")
        elif item.change_rate and float(item.change_rate) < -5:
            reasons.append("超跌反弹机会")
    except (ValueError, TypeError):
        pass

    # 成交量分析
    try:
        if item.volume_ratio and float(item.volume_ratio) > 2:
            reasons.append("成交量异常放大")
        elif item.volume_ratio and float(item.volume_ratio) < 0.5:
            reasons.append("缩量整理")
    except (ValueError, TypeError):
        pass

    # 均线支撑分析
    try:
        if item.ma5 and item.ma20 and float(item.ma5) > float(item.ma20):
            reasons.append("MA5>MA20多头")
        elif item.ma10 and item.ma20 and float(item.ma10) > float(item.ma20):
            reasons.append("短期均线上行")
    except (ValueError, TypeError):
        pass

    if not reasons:
        return "技术面偏强"

    return "、".join(reasons[:3])


def _generate_sell_reason(item) -> str:
    """生成卖出理由"""
    reasons = []

    # 均线空头排列
    if getattr(item, 'short_avg_array', None) == '1':
        reasons.append("均线空头排列")

    # 高位资金净流出
    if getattr(item, 'high_funds_outflow', None) == '1':
        reasons.append("高位资金净流出")

    # 连涨放量
    if getattr(item, 'upper_large_volume', None) == '1':
        reasons.append("高位放量滞涨")

    # K线形态卖出信号
    if getattr(item, 'shooting_star', None) == '1':
        reasons.append("射击之星")
    elif getattr(item, 'evening_star', None) == '1':
        reasons.append("黄昏之星")
    elif getattr(item, 'black_cloud_tops', None) == '1':
        reasons.append("乌云盖顶")
    elif getattr(item, 'bearish_engulfing', None) == '1':
        reasons.append("穿头破脚")
    elif getattr(item, 'down_7days', None) == '1':
        reasons.append("七连阴")

    # 趋势位置分析
    try:
        if item.change_rate and float(item.change_rate) < -5:
            reasons.append("大幅下跌")
        elif item.change_rate and float(item.change_rate) > 5:
            reasons.append("追高风险")
    except (ValueError, TypeError):
        pass

    # 成交量分析
    try:
        if item.volume_ratio and float(item.volume_ratio) > 2:
            reasons.append("放量下跌")
        elif item.volume_ratio and float(item.volume_ratio) < 0.5:
            reasons.append("缩量下跌动能不足")
    except (ValueError, TypeError):
        pass

    # 均线压力分析
    try:
        if item.ma5 and item.ma20 and float(item.ma5) < float(item.ma20):
            reasons.append("MA5<MA20空头")
        elif item.ma10 and item.ma20 and float(item.ma10) < float(item.ma20):
            reasons.append("短期均线下行")
    except (ValueError, TypeError):
        pass

    if not reasons:
        return "技术面偏弱"

    return "、".join(reasons[:3])


def _filter_buy_signals(results: List) -> List:
    """
    筛选买入信号股票

    基于技术指标筛选：
    - MACD金叉
    - KDJ金叉
    - 放量突破
    - 均线多头排列
    """
    filtered = []
    for item in results:
        # 过滤ST股票
        if _is_st_stock(getattr(item, 'name', None)):
            continue

        # 检查买入信号
        has_buy_signal = False

        # MACD金叉信号
        if getattr(item, 'macd_golden_fork', None) == '1':
            has_buy_signal = True
        # KDJ金叉信号
        elif getattr(item, 'kdj_golden_fork', None) == '1':
            has_buy_signal = True
        # 放量突破信号
        elif getattr(item, 'break_through', None) == '1':
            has_buy_signal = True
        # 均线多头排列
        elif getattr(item, 'long_avg_array', None) == '1':
            has_buy_signal = True
        # 低位资金净流入
        elif getattr(item, 'low_funds_inflow', None) == '1':
            has_buy_signal = True
        # 向上突破均线
        elif getattr(item, 'breakup_ma_5days', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'breakup_ma_10days', None) == '1':
            has_buy_signal = True
        # K线形态买入信号
        elif getattr(item, 'one_dayang_line', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'two_dayang_lines', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'rise_sun', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'power_fulgun', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'morning_star', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'first_dawn', None) == '1':
            has_buy_signal = True
        elif getattr(item, 'reversing_hammer', None) == '1':
            has_buy_signal = True

        if has_buy_signal:
            filtered.append(item)

    return filtered


def _filter_sell_signals(results: List) -> List:
    """
    筛选卖出信号股票

    基于技术指标筛选：
    - 均线空头排列
    - 高位资金净流出
    - K线形态卖出信号
    """
    filtered = []
    for item in results:
        # 过滤ST股票
        if _is_st_stock(getattr(item, 'name', None)):
            continue

        # 检查卖出信号
        has_sell_signal = False

        # 均线空头排列
        if getattr(item, 'short_avg_array', None) == '1':
            has_sell_signal = True
        # 高位资金净流出
        elif getattr(item, 'high_funds_outflow', None) == '1':
            has_sell_signal = True
        # 连涨放量（可能见顶）
        elif getattr(item, 'upper_large_volume', None) == '1':
            has_sell_signal = True
        # K线形态卖出信号
        elif getattr(item, 'shooting_star', None) == '1':
            has_sell_signal = True
        elif getattr(item, 'evening_star', None) == '1':
            has_sell_signal = True
        elif getattr(item, 'black_cloud_tops', None) == '1':
            has_sell_signal = True
        elif getattr(item, 'bearish_engulfing', None) == '1':
            has_sell_signal = True
        elif getattr(item, 'down_7days', None) == '1':
            has_sell_signal = True

        if has_sell_signal:
            filtered.append(item)

    return filtered


def _format_stock_data(items: List, is_buy: bool = True) -> List[Dict]:
    """格式化股票数据为返回格式"""
    formatted = []
    for item in items:
        formatted.append({
            "code": str(item.code).strip(),
            "name": str(item.name).strip(),
            "reason": _generate_buy_reason(item) if is_buy else _generate_sell_reason(item),
            "new_price": item.new_price,
            "change_rate": item.change_rate,
            "volume_ratio": item.volume_ratio,
            "high_price": item.high_price,
            "low_price": item.low_price,
            "pre_close_price": item.pre_close_price,
            "volume": item.volume,
            "deal_amount": item.deal_amount,
            "turnoverrate": item.turnoverrate,
            "listing_date": item.listing_date.isoformat() if item.listing_date else None,
            "industry": str(item.industry).strip() if item.industry else None,
            "area": str(item.area).strip() if item.area else None,
            "concept": str(item.concept).strip() if item.concept else None,
            "pe": item.pe,
            "pbnewmrq": item.pbnewmrq,
            "total_market_cap": item.total_market_cap,
            "free_cap": item.free_cap,
            "ma5": item.ma5,
            "ma10": item.ma10,
            "ma20": item.ma20,
            "ma60": item.ma60,
            "ma120": item.ma120,
            "ma250": item.ma250,
            # 信号标记
            "macd_golden_fork": str(item.macd_golden_fork).strip() if item.macd_golden_fork else None,
            "kdj_golden_fork": str(item.kdj_golden_fork).strip() if item.kdj_golden_fork else None,
            "break_through": str(item.break_through).strip() if item.break_through else None,
            "long_avg_array": str(item.long_avg_array).strip() if item.long_avg_array else None,
            "short_avg_array": str(item.short_avg_array).strip() if item.short_avg_array else None,
            "low_funds_inflow": str(item.low_funds_inflow).strip() if item.low_funds_inflow else None,
            "high_funds_outflow": str(item.high_funds_outflow).strip() if item.high_funds_outflow else None,
            "upper_large_volume": str(item.upper_large_volume).strip() if getattr(item, 'upper_large_volume', None) else None,
            "shooting_star": str(item.shooting_star).strip() if getattr(item, 'shooting_star', None) else None,
            "evening_star": str(item.evening_star).strip() if getattr(item, 'evening_star', None) else None,
            "black_cloud_tops": str(item.black_cloud_tops).strip() if getattr(item, 'black_cloud_tops', None) else None,
            "bearish_engulfing": str(item.bearish_engulfing).strip() if getattr(item, 'bearish_engulfing', None) else None,
            "down_7days": str(item.down_7days).strip() if getattr(item, 'down_7days', None) else None,
        })
    return formatted


@router.get(
    "/",
    responses={
        200: {"description": "买入信号股票数据"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取买入信号股票",
    description="基于技术指标筛选出具有买入信号的股票"
)
def get_buy_stocks(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort_field: str = Query("change_rate", description="排序字段：change_rate/volume/deal_amount"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    keyword: Optional[str] = Query(None, description="关键字搜索，匹配代码/名称"),
    industry: Optional[str] = Query(None, description="行业筛选"),
):
    """
    获取买入信号股票

    基于以下技术指标筛选：
    - MACD金叉
    - KDJ金叉
    - 放量突破
    - 均线多头排列
    - 低位资金净流入
    - 向上突破均线
    - K线形态（大阳线、旭日东升、多方炮、早晨之星等）
    """
    try:
        repo = SelectionRepository()

        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = DateType.today()

        # 检查是否为交易日
        trading_day = is_trading_day(query_date)
        notice_message = None

        if not trading_day:
            notice_message = f"{query_date.strftime('%Y-%m-%d')} 是非交易日（周末或节假日），暂无买入信号"
            results = []
        else:
            results = repo.get_or_fetch(query_date)
            # 应用买入信号筛选（已包含ST过滤）
            results = _filter_buy_signals(results)

        # 关键字过滤（支持正则表达式）
        if keyword:
            keyword_pattern = keyword.strip()
            results = [r for r in results if
                       _regex_match(str(r.code), keyword_pattern) or
                       _regex_match(str(r.name), keyword_pattern)]

        # 行业过滤
        if industry:
            industry_lower = industry.lower().strip()
            results = [r for r in results if r.industry and industry_lower in str(r.industry).lower()]

        # 排序
        sort_key = sort_field
        reverse = sort_order.lower() == 'desc'
        results.sort(key=lambda x: (getattr(x, sort_key, 0) or 0), reverse=reverse)

        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]

        formatted_data = _format_stock_data(paginated_results, is_buy=True)

        return {
            "date": query_date.isoformat(),
            "count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "data": formatted_data,
            "is_trading_day": trading_day,
            "message": notice_message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取买入信号股票失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取买入信号股票失败: {str(e)}"
            }
        )


@sell_router.get(
    "/",
    responses={
        200: {"description": "卖出信号股票数据"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取卖出信号股票",
    description="基于技术指标筛选出具有卖出信号的股票"
)
def get_sell_stocks(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort_field: str = Query("change_rate", description="排序字段：change_rate/volume/deal_amount"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    keyword: Optional[str] = Query(None, description="关键字搜索，匹配代码/名称"),
    industry: Optional[str] = Query(None, description="行业筛选"),
):
    """
    获取卖出信号股票

    基于以下技术指标筛选：
    - 均线空头排列
    - 高位资金净流出
    - K线形态（射击之星、黄昏之星、乌云盖顶、穿头破脚、七连阴等）
    """
    try:
        repo = SelectionRepository()

        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = DateType.today()

        # 检查是否为交易日
        trading_day = is_trading_day(query_date)
        notice_message = None

        if not trading_day:
            notice_message = f"{query_date.strftime('%Y-%m-%d')} 是非交易日（周末或节假日），暂无卖出信号"
            results = []
        else:
            results = repo.get_or_fetch(query_date)
            # 应用卖出信号筛选（已包含ST过滤）
            results = _filter_sell_signals(results)

        # 关键字过滤（支持正则表达式）
        if keyword:
            keyword_pattern = keyword.strip()
            results = [r for r in results if
                       _regex_match(str(r.code), keyword_pattern) or
                       _regex_match(str(r.name), keyword_pattern)]

        # 行业过滤
        if industry:
            industry_lower = industry.lower().strip()
            results = [r for r in results if r.industry and industry_lower in str(r.industry).lower()]

        # 排序
        sort_key = sort_field
        reverse = sort_order.lower() == 'desc'
        results.sort(key=lambda x: (getattr(x, sort_key, 0) or 0), reverse=reverse)

        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]

        formatted_data = _format_stock_data(paginated_results, is_buy=False)

        return {
            "date": query_date.isoformat(),
            "count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "data": formatted_data,
            "is_trading_day": trading_day,
            "message": notice_message
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取卖出信号股票失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取卖出信号股票失败: {str(e)}"
            }
        )