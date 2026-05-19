# -*- coding: utf-8 -*-
"""
===================================
涨停数据接口
===================================

职责：
1. GET /api/v1/limitup 获取涨停数据
"""

import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.v1.schemas.common import ErrorResponse
from src.repositories.limitup_repo import LimitUpRepository

logger = logging.getLogger(__name__)


def is_trading_day(check_date: date) -> bool:
    """
    检查是否为交易日（中国A股）

    Args:
        check_date: 要检查的日期

    Returns:
        是否为交易日（周一到周五返回True，周六周日返回False）
    """
    return check_date.weekday() < 5

router = APIRouter()


@router.get(
    "/",
    responses={
        200: {"description": "涨停数据"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取涨停数据",
    description="获取指定日期的涨停股票数据，包含涨停原因、换手率、成交量等信息"
)
def get_limit_up_data(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort_field: str = Query("change_pct", description="排序字段：turnover_rate/volume/amount/change_pct"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    keyword: Optional[str] = Query(None, description="关键字搜索，匹配代码/名称/原因/详因")
):
    """
    获取涨停数据

    获取指定日期的涨停股票数据，数据来源于同花顺 API，支持数据库缓存

    Args:
        date: 日期（YYYY-MM-DD），默认当天
        page: 页码，从1开始
        page_size: 每页条数，最大100条
        sort_field: 排序字段，支持 turnover_rate/volume/amount/change_pct
        sort_order: 排序方式，asc（升序）或 desc（降序）
        keyword: 关键字搜索，匹配代码/名称/原因/详因

    Returns:
        包含日期、分页信息和股票列表的字典

    Raises:
        HTTPException: 500 - 获取数据失败
    """
    try:
        repo = LimitUpRepository()

        # 使用指定日期或默认当天
        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = date.today()

        # 检查是否为交易日（非交易日返回空数据）
        if not is_trading_day(query_date):
            return {
                "date": query_date.strftime('%Y-%m-%d'),
                "count": 0,
                "total_pages": 0,
                "current_page": 1,
                "page_size": page_size,
                "data": [],
                "is_trading_day": False,
                "message": f"{query_date.strftime('%Y-%m-%d')} 是非交易日（周末或节假日），暂无涨停数据"
            }

        # 获取数据（优先从数据库，不存在则从数据源获取）
        results = repo.get_or_fetch(query_date)

        # 关键字过滤
        if keyword and keyword.strip():
            keyword_lower = keyword.lower().strip()
            filtered_results = []
            for item in results:
                code = str(item.code or '').lower()
                name = str(item.name or '').lower()
                title = str(item.title or '').lower()
                reason = str(item.reason or '').lower()
                if (keyword_lower in code or
                    keyword_lower in name or
                    keyword_lower in title or
                    keyword_lower in reason):
                    filtered_results.append(item)
            results = filtered_results

        # 排序字段映射
        field_mapping = {
            'turnover_rate': 'turnoverrate',
            'volume': 'volume',
            'amount': 'deal_amount',
            'change_pct': 'change_rate'
        }
        
        # 验证排序字段
        if sort_field not in field_mapping:
            sort_field = 'change_pct'
        
        # 排序
        sort_key = field_mapping[sort_field]
        reverse = sort_order.lower() == 'desc'
        
        # 使用正确的排序逻辑，确保获取实际值
        results.sort(key=lambda x: (getattr(x, sort_key) or 0), reverse=reverse)
        
        # 计算分页
        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size
        
        # 计算切片范围
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        # 格式化数据
        formatted_data = []
        for item in paginated_results:
            formatted_data.append({
                "code": str(item.code).strip(),
                "name": str(item.name).strip(),
                "reason": str(item.title or "").strip(),
                "detail_reason": str(item.reason or "").strip(),
                "turnover_rate": item.turnoverrate,
                "volume": item.volume,
                "amount": item.deal_amount,
                "change_pct": item.change_rate,
                "price": item.new_price,
                "ups_downs": item.ups_downs,
                "dde": item.dde,
            })
        
        return {
            "date": query_date.isoformat(),
            "count": total_count,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "data": formatted_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取涨停数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取涨停数据失败: {str(e)}"
            }
        )


@router.post(
    "/fetch",
    responses={
        200: {"description": "数据获取成功"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="手动触发获取涨停数据",
    description="手动触发从数据源获取指定日期的涨停数据并保存到数据库"
)
def fetch_limit_up_data(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    手动触发获取涨停数据
    
    从同花顺 API 获取指定日期的涨停数据并保存到数据库
    
    Args:
        date: 日期（YYYY-MM-DD），默认当天
        
    Returns:
        保存的记录数
        
    Raises:
        HTTPException: 500 - 获取数据失败
    """
    try:
        repo = LimitUpRepository()
        
        # 使用指定日期或默认当天
        if date:
            try:
                query_date = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = date.today()
        
        # 从数据源获取并保存
        count = repo.save_from_fetcher(query_date)
        
        return {
            "date": query_date.isoformat(),
            "saved_count": count,
            "message": f"成功获取并保存 {count} 条涨停数据"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手动获取涨停数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取涨停数据失败: {str(e)}"
            }
        )
