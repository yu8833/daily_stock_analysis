# -*- coding: utf-8 -*-
"""
===================================
MarketData Endpoints - 市场数据接口
===================================

提供早盘、尾盘抢筹数据接口
"""

import logging
from datetime import date as DateType
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

from src.repositories import (
    ChipRaceRepository,
)

router = APIRouter()


class ChipRaceItem(BaseModel):
    """抢筹数据项"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    date: DateType = Field(..., description="日期")
    period: int = Field(..., description="周期类型，0=早盘，1=尾盘")
    latest_price: Optional[float] = Field(None, description="最新价")
    change_pct: Optional[float] = Field(None, description="涨跌幅")
    prev_close: Optional[float] = Field(None, description="昨收")
    open_price: Optional[float] = Field(None, description="今开")
    amount: Optional[float] = Field(None, description="开盘/收盘金额")
    race_amount: Optional[float] = Field(None, description="抢筹成交金额")
    race_ratio: Optional[float] = Field(None, description="抢筹占比")
    race_pct: Optional[float] = Field(None, description="抢筹幅度")
    board_days: Optional[int] = Field(None, description="连板天数")
    board_type: Optional[str] = Field(None, description="板类型")


# ==================== 抢筹数据接口 ====================

@router.get("/zpqc", response_model=List[ChipRaceItem], tags=["MarketData"])
def get_race_open(
    query_date: Optional[DateType] = Query(None, description="查询日期")
):
    """获取早盘抢筹数据（zpqc）"""
    try:
        repo = ChipRaceRepository()
        results = repo.get_or_fetch_open(query_date)
        
        return [
            ChipRaceItem(
                code=r.code,
                name=r.name,
                date=r.date,
                period=r.period,
                latest_price=r.latest_price,
                change_pct=r.change_pct,
                prev_close=r.prev_close,
                open_price=r.open_price,
                amount=r.amount,
                race_amount=r.race_amount,
                race_ratio=r.race_ratio,
                race_pct=r.race_pct,
                board_days=r.board_days,
                board_type=r.board_type,
            ) for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wpqc", response_model=List[ChipRaceItem], tags=["MarketData"])
def get_race_close(
    query_date: Optional[DateType] = Query(None, description="查询日期")
):
    """获取尾盘抢筹数据（wpqc）"""
    try:
        repo = ChipRaceRepository()
        results = repo.get_or_fetch_close(query_date)
        
        return [
            ChipRaceItem(
                code=r.code,
                name=r.name,
                date=r.date,
                period=r.period,
                latest_price=r.latest_price,
                change_pct=r.change_pct,
                prev_close=r.prev_close,
                open_price=r.open_price,
                amount=r.amount,
                race_amount=r.race_amount,
                race_ratio=r.race_ratio,
                race_pct=r.race_pct,
                board_days=r.board_days,
                board_type=r.board_type,
            ) for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))