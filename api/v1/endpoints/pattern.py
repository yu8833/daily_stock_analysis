# -*- coding: utf-8 -*-
"""
===================================
K线形态识别接口
===================================

职责：
1. GET /api/v1/pattern/{code} 获取指定股票的K线形态
2. GET /api/v1/pattern/list 获取所有K线形态列表
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

KLINE_PATTERNS = {
    "tow_crows": {"cn": "两只乌鸦", "en": "Two Crows"},
    "upside_gap_two_crows": {"cn": "向上跳空的两只乌鸦", "en": "Upside Gap Two Crows"},
    "three_black_crows": {"cn": "三只乌鸦", "en": "Three Black Crows"},
    "identical_three_crows": {"cn": "三胞胎乌鸦", "en": "Identical Three Crows"},
    "three_line_strike": {"cn": "三线打击", "en": "Three Line Strike"},
    "dark_cloud_cover": {"cn": "乌云压顶", "en": "Dark Cloud Cover"},
    "evening_doji_star": {"cn": "十字暮星", "en": "Evening Doji Star"},
    "doji_star": {"cn": "十字星", "en": "Doji Star"},
    "hanging_man": {"cn": "上吊线", "en": "Hanging Man"},
    "hikkake_pattern": {"cn": "陷阱", "en": "Hikkake Pattern"},
    "modified_hikkake_pattern": {"cn": "修正陷阱", "en": "Modified Hikkake"},
    "in_neck_pattern": {"cn": "颈内线", "en": "In Neck Pattern"},
    "on_neck_pattern": {"cn": "颈上线", "en": "On Neck Pattern"},
    "thrusting_pattern": {"cn": "插入", "en": "Thrusting Pattern"},
    "shooting_star": {"cn": "射击之星", "en": "Shooting Star"},
    "stalled_pattern": {"cn": "停顿形态", "en": "Stalled Pattern"},
    "advance_block": {"cn": "大敌当前", "en": "Advance Block"},
    "high_wave_candle": {"cn": "风高浪大线", "en": "High Wave Candle"},
    "engulfing_pattern": {"cn": "吞噬模式", "en": "Engulfing Pattern"},
    "abandoned_baby": {"cn": "弃婴", "en": "Abandoned Baby"},
    "closing_marubozu": {"cn": "收盘缺影线", "en": "Closing Marubozu"},
    "doji": {"cn": "十字", "en": "Doji"},
    "up_down_gap": {"cn": "向上/下跳空并列阳线", "en": "Up/Down Gap"},
    "long_legged_doji": {"cn": "长脚十字", "en": "Long Legged Doji"},
    "rickshaw_man": {"cn": "黄包车夫", "en": "Rickshaw Man"},
    "marubozu": {"cn": "光头光脚/缺影线", "en": "Marubozu"},
    "three_inside_up_down": {"cn": "三内部上涨和下跌", "en": "Three Inside Up/Down"},
    "three_outside_up_down": {"cn": "三外部上涨和下跌", "en": "Three Outside Up/Down"},
    "three_stars_in_the_south": {"cn": "南方三星", "en": "Three Stars in the South"},
    "three_white_soldiers": {"cn": "三个白兵", "en": "Three White Soldiers"},
    "belt_hold": {"cn": "捉腰带线", "en": "Belt Hold"},
    "breakaway": {"cn": "脱离", "en": "Breakaway"},
    "concealing_baby_swallow": {"cn": "藏婴吞没", "en": "Concealing Baby Swallow"},
    "counterattack": {"cn": "反击线", "en": "Counterattack"},
    "dragonfly_doji": {"cn": "蜻蜓十字/T形十字", "en": "Dragonfly Doji"},
    "evening_star": {"cn": "暮星", "en": "Evening Star"},
    "gravestone_doji": {"cn": "墓碑十字/倒T十字", "en": "Gravestone Doji"},
    "hammer": {"cn": "锤头", "en": "Hammer"},
    "harami_pattern": {"cn": "母子线", "en": "Harami Pattern"},
    "harami_cross_pattern": {"cn": "十字孕线", "en": "Harami Cross Pattern"},
    "homing_pigeon": {"cn": "家鸽", "en": "Homing Pigeon"},
    "inverted_hammer": {"cn": "倒锤头", "en": "Inverted Hammer"},
    "kicking": {"cn": "反冲形态", "en": "Kicking"},
    "kicking_bull_bear": {"cn": "由较长缺影线决定的反冲形态", "en": "Kicking by Length"},
    "ladder_bottom": {"cn": "梯底", "en": "Ladder Bottom"},
    "long_line_candle": {"cn": "长蜡烛", "en": "Long Line Candle"},
    "matching_low": {"cn": "相同低价", "en": "Matching Low"},
    "mat_hold": {"cn": "铺垫", "en": "Mat Hold"},
    "morning_doji_star": {"cn": "十字晨星", "en": "Morning Doji Star"},
    "morning_star": {"cn": "晨星", "en": "Morning Star"},
    "piercing_pattern": {"cn": "刺透形态", "en": "Piercing Pattern"},
    "rising_falling_three": {"cn": "上升/下降三法", "en": "Rise/Fall Three Methods"},
    "separating_lines": {"cn": "分离线", "en": "Separating Lines"},
    "short_line_candle": {"cn": "短蜡烛", "en": "Short Line Candle"},
    "spinning_top": {"cn": "纺锤", "en": "Spinning Top"},
    "stick_sandwich": {"cn": "条形三明治", "en": "Stick Sandwich"},
    "takuri": {"cn": "探水竿", "en": "Takuri"},
    "tasuki_gap": {"cn": "跳空并列阴阳线", "en": "Tasuki Gap"},
    "tristar_pattern": {"cn": "三星", "en": "Tristar Pattern"},
    "unique_3_river": {"cn": "奇特三河床", "en": "Unique 3 River"},
    "upside_downside_gap": {"cn": "上升/下降跳空三法", "en": "Upside/Downside Gap 3 Methods"},
}


class PatternItem(BaseModel):
    code: str
    name: str
    pattern_key: str
    pattern_cn: str
    pattern_en: str
    direction: str
    date: str
    position: int


class PatternListResponse(BaseModel):
    patterns: list
    total: int


@router.get(
    "/list",
    response_model=PatternListResponse,
    summary="获取K线形态列表",
    description="获取所有支持的K线形态列表"
)
async def get_pattern_list():
    """
    获取所有支持的K线形态列表
    """
    patterns = []
    for key, info in KLINE_PATTERNS.items():
        patterns.append({
            "key": key,
            "cn": info["cn"],
            "en": info["en"]
        })
    
    return {
        "patterns": patterns,
        "total": len(patterns)
    }


@router.get(
    "/{code}",
    summary="获取股票K线形态",
    description="获取指定股票的K线形态识别结果"
)
async def get_stock_patterns(
    code: str,
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    获取指定股票的K线形态识别结果
    
    注意：此接口需要talib库支持。如未安装，将返回提示信息。
    """
    try:
        import talib
        import numpy as np
        from data_provider import DataFetcherManager
        
        provider = DataFetcherManager()
        
        result = provider.get_daily_data(code, days=120)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail={"error": "not_found", "message": f"未找到股票 {code} 的历史数据"}
            )
        
        stock_data = result[0] if isinstance(result, tuple) else result
        if stock_data is None or len(stock_data) == 0:
            raise HTTPException(
                status_code=404,
                detail={"error": "not_found", "message": f"未找到股票 {code} 的历史数据"}
            )
        
        if 'date' not in stock_data.columns:
            stock_data['date'] = stock_data.index
        
        open_prices = np.array(stock_data['open'].values, dtype=float)
        high_prices = np.array(stock_data['high'].values, dtype=float)
        low_prices = np.array(stock_data['low'].values, dtype=float)
        close_prices = np.array(stock_data['close'].values, dtype=float)
        dates = stock_data['date'].values
        
        stock_name = code
        
        results = []
        
        for pattern_key, pattern_info in KLINE_PATTERNS.items():
            func_name = f"CDL{pattern_key.upper().replace('_', '')}"
            if not hasattr(talib, func_name):
                continue
            
            func = getattr(talib, func_name)
            try:
                result = func(open_prices, high_prices, low_prices, close_prices)
                
                for i, value in enumerate(result):
                    if value != 0:
                        direction = "看跌" if value < 0 else "看涨"
                        date_val = dates[i]
                        if hasattr(date_val, 'strftime'):
                            date_str = date_val.strftime('%Y-%m-%d')
                        elif isinstance(date_val, str):
                            date_str = date_val.split(' ')[0].split('T')[0]
                        else:
                            date_str = str(date_val).split(' ')[0].split('T')[0]
                        
                        results.append({
                            "code": code,
                            "name": stock_name,
                            "pattern_key": pattern_key,
                            "pattern_cn": pattern_info["cn"],
                            "pattern_en": pattern_info["en"],
                            "direction": direction,
                            "date": date_str,
                            "position": int(i)
                        })
            except Exception as e:
                logger.warning(f"Pattern {pattern_key} failed for {code}: {e}")
                continue
        
        results.sort(key=lambda x: x["date"], reverse=True)
        
        return {
            "code": code,
            "name": results[0]["name"] if results else code,
            "patterns": results,
            "total": len(results)
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "dependency_missing",
                "message": "talib库未安装，无法进行K线形态识别。请联系管理员安装ta-lib库。"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取K线形态失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": f"获取K线形态失败: {str(e)}"}
        )