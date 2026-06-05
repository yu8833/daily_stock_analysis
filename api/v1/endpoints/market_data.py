# -*- coding: utf-8 -*-
"""
===================================
MarketData Endpoints - 市场数据接口
===================================

提供市场数据接口（已移除抢筹数据）
"""

import logging
from typing import List

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()

# ==================== 市场数据接口 ====================

# 抢筹数据接口已移除，现在使用信号接口替代
# 买入信号：/api/v1/signals/buy
# 卖出信号：/api/v1/signals/sell