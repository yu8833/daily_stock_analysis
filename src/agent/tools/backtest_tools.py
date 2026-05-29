# -*- coding: utf-8 -*-
"""
Backtest tools — wraps backtest service as agent-callable tools.

Tools:
- get_skill_backtest_summary: Get backtest summary for a specific skill
- get_stock_backtest_summary: Get backtest data for a specific stock
"""

import logging
from typing import Optional

from src.agent.tools.registry import ToolParameter, ToolDefinition

logger = logging.getLogger(__name__)


def _get_backtest_service():
    """Get backtest service instance (lazy import to avoid circular dependencies)."""
    try:
        from src.services.backtest_service import BacktestService
        return BacktestService()
    except ImportError:
        logger.warning("BacktestService not available, returning mock service")
        return None


def _handle_get_skill_backtest_summary(skill_id: str, eval_window_days: Optional[int] = 20) -> dict:
    """Get backtest summary for a specific skill."""
    if not (skill_id and str(skill_id).strip()):
        return {
            "supported": False,
            "error": "skill_id is required. Use get_strategy_backtest_summary for overall metrics."
        }
    
    svc = _get_backtest_service()
    if svc is None:
        return {
            "supported": False,
            "error": "Backtest service not available."
        }
    
    try:
        result = svc.get_skill_summary(skill_id=skill_id, eval_window_days=eval_window_days)
        
        if result is None:
            return {
                "supported": False,
                "error": f"No backtest data available for skill: {skill_id}"
            }
        
        return {
            "scope": "skill",
            "skill_id": skill_id,
            "supported": True,
            "eval_window_days": result.get("eval_window_days", eval_window_days),
            "total_evaluations": result.get("total_evaluations", 0),
            "completed_count": result.get("completed_count", 0),
            "win_rate": result.get("win_rate"),
            "direction_accuracy": result.get("direction_accuracy"),
            "avg_return": result.get("avg_return"),
            "win_rate_pct": round(result.get("win_rate", 0) * 100, 1) if result.get("win_rate") else None,
            "direction_accuracy_pct": round(result.get("direction_accuracy", 0) * 100, 1) if result.get("direction_accuracy") else None,
            "avg_stock_return_pct": round(result.get("avg_stock_return", 0) * 100, 1) if result.get("avg_stock_return") else None,
            "avg_simulated_return_pct": round(result.get("avg_return", 0) * 100, 1) if result.get("avg_return") else None,
            "computed_at": result.get("computed_at"),
        }
    except Exception:
        logger.error(f"Failed to get skill backtest summary for {skill_id}", exc_info=True)
        return {"error": "Failed to retrieve backtest summary."}


def _handle_get_stock_backtest_summary(stock_code: str) -> dict:
    """Get backtest data for a specific stock."""
    if not (stock_code and str(stock_code).strip()):
        return {"error": "stock_code is required"}
    
    svc = _get_backtest_service()
    if svc is None:
        return {
            "supported": False,
            "error": "Backtest service not available."
        }
    
    try:
        result = svc.get_summary(stock_code=stock_code)
        
        if result is None:
            return {
                "supported": False,
                "error": f"No backtest data available for stock: {stock_code}"
            }
        
        return {
            "scope": "stock",
            "stock_code": stock_code,
            "supported": True,
            **result
        }
    except Exception:
        logger.error(f"Failed to get stock backtest summary for {stock_code}", exc_info=True)
        return {"error": "Failed to retrieve backtest data."}


get_skill_backtest_summary_tool = ToolDefinition(
    name="get_skill_backtest_summary",
    description="Get backtest performance summary for a specific trading skill/strategy. Returns win rate, accuracy, and return metrics.",
    parameters=[
        ToolParameter(
            name="skill_id",
            type="string",
            description="The ID of the skill/strategy to query (e.g., 'bull_trend', 'breakout')",
            required=True
        ),
        ToolParameter(
            name="eval_window_days",
            type="integer",
            description="Evaluation window in days (default: 20)",
            required=False
        )
    ],
    handler=_handle_get_skill_backtest_summary
)


get_stock_backtest_summary_tool = ToolDefinition(
    name="get_stock_backtest_summary",
    description="Get backtest data for a specific stock, including historical performance and metrics.",
    parameters=[
        ToolParameter(
            name="stock_code",
            type="string",
            description="The stock code to query (e.g., '600519', '000001')",
            required=True
        )
    ],
    handler=_handle_get_stock_backtest_summary
)


ALL_BACKTEST_TOOLS = [
    get_skill_backtest_summary_tool,
    get_stock_backtest_summary_tool,
]