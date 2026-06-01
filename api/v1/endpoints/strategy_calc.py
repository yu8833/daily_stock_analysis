# -*- coding: utf-8 -*-
"""
===================================
策略计算接口
===================================

职责：
1. 手动触发策略计算任务
2. 查询策略计算任务状态
"""

import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.v1.schemas.common import ErrorResponse
from src.services.task_queue import get_task_queue
from src.services.strategy_calculation import run_strategy_calculation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategy-calc", tags=["策略计算"])


@router.post(
    "/calculate",
    responses={
        200: {"description": "策略计算任务已提交"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="触发策略计算",
    description="为指定日期的股票批量计算需要历史数据的策略信号"
)
def trigger_strategy_calculation(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天"),
):
    """
    触发策略计算任务
    
    该任务会异步计算以下策略：
    - 停机坪
    - 无大幅回撤
    - 海龟交易法则
    - 宽而窄的旗形
    - 低ATR成长
    
    注意：由于需要获取每只股票的历史数据，此任务可能需要较长时间完成
    """
    try:
        if date:
            try:
                query_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={"error": "invalid_date", "message": "日期格式错误，应为 YYYY-MM-DD"}
                )
        else:
            query_date = date.today()
        
        # 创建后台任务
        task_queue = get_task_queue()
        
        def task_func():
            return run_strategy_calculation(query_date)
        
        task_info = task_queue.submit_background_task(
            run_task=task_func,
            stock_code="STRATEGY_CALC",
            stock_name="策略计算",
            report_type="strategy",
            message=f"开始计算 {query_date} 的策略信号"
        )
        
        logger.info(f"[StrategyAPI] 策略计算任务已提交: {task_info.task_id}")
        
        return {
            "task_id": task_info.task_id,
            "date": query_date.strftime("%Y-%m-%d"),
            "status": task_info.status.value,
            "message": task_info.message,
            "created_at": task_info.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[StrategyAPI] 触发策略计算失败: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "internal_error", "message": str(e)}
        )


@router.get(
    "/tasks/{task_id}",
    responses={
        200: {"description": "任务状态"},
        404: {"description": "任务不存在", "model": ErrorResponse},
    },
    summary="查询策略计算任务状态",
)
def get_strategy_task_status(task_id: str):
    """
    查询策略计算任务的状态
    
    Args:
        task_id: 任务ID
    """
    task_queue = get_task_queue()
    task = task_queue.get_task(task_id)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail={"error": "task_not_found", "message": "任务不存在"}
        )
    
    return task.to_dict()


@router.get(
    "/tasks",
    responses={
        200: {"description": "任务列表"},
    },
    summary="获取策略计算任务列表",
)
def list_strategy_tasks(limit: int = Query(10, ge=1, le=50)):
    """
    获取策略计算任务列表（按创建时间倒序）
    
    Args:
        limit: 返回数量限制
    """
    task_queue = get_task_queue()
    tasks = task_queue.list_all_tasks(limit=limit)
    
    # 过滤策略计算任务
    strategy_tasks = [
        task.to_dict() for task in tasks 
        if task.stock_code == "STRATEGY_CALC"
    ]
    
    return {
        "count": len(strategy_tasks),
        "tasks": strategy_tasks
    }