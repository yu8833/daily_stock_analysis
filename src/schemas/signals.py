# -*- coding: utf-8 -*-
from typing import List, Optional
from pydantic import BaseModel

class SignalScanResult(BaseModel):
    stock_code: str
    stock_name: str
    signal_type: str
    signal_name: str
    score: int
    recommendation: str

class StockAnalysis(BaseModel):
    stock_code: str
    stock_name: str
    current_price: float
    ma_5: Optional[float]
    ma_8: Optional[float]
    ma_13: Optional[float]
    ma_55: Optional[float]
    ma_60: Optional[float]
    ma_65: Optional[float]
    bias_60: float
    dif: Optional[float]
    dea: Optional[float]
    macd_bar: Optional[float]
    g: float
    delta_g: float
    quadrant: str
    signals: List[str]
    signal_score: int