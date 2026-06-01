# -*- coding: utf-8 -*-
"""
===================================
数据导出API
===================================

职责：
1. 提供股票数据导出功能
2. 支持CSV、Excel格式
3. 提供批量导出选项
"""

import io
import csv
import logging
from datetime import datetime
from typing import Optional, List, Any, Dict
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["Export"])


def generate_csv(data: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    """
    生成CSV文件流式响应
    
    Args:
        data: 数据列表
        filename: 文件名
        
    Returns:
        流式响应
    """
    if not data:
        raise HTTPException(status_code=404, detail="没有数据可导出")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


def generate_excel(data: List[Dict[str, Any]], filename: str) -> StreamingResponse:
    """
    生成Excel文件流式响应
    
    Args:
        data: 数据列表
        filename: 文件名
        
    Returns:
        流式响应
    """
    if not data:
        raise HTTPException(status_code=404, detail="没有数据可导出")
    
    try:
        import pandas as pd
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#2196F3',
                'color': 'white'
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            worksheet.autofilter(0, 0, 0, len(df.columns) - 1)
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).apply(len).max(), len(str(col)))
                worksheet.set_column(i, i, min(max_len + 2, 50))
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="Excel导出功能需要安装pandas和xlsxwriter"
        )


@router.get("/selection", summary="导出选股数据", description="导出当前选股结果")
async def export_selection(
    format: str = Query("csv", description="导出格式: csv 或 excel"),
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD")
):
    """导出选股数据"""
    from src.repositories.selection_repo import SelectionRepository
    
    try:
        repo = SelectionRepository()
        
        if date:
            query_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            query_date = datetime.now().date()
        
        stocks = repo.get_by_date(query_date)
        
        export_data = []
        for stock in stocks:
            export_data.append({
                "代码": stock.code,
                "名称": stock.name,
                "最新价": stock.new_price or "",
                "涨跌幅": stock.pct_chg or "",
                "成交量": stock.volume or "",
                "成交额": stock.amount or "",
                "换手率": stock.turnoverrate or "",
                "市盈率": stock.pe or "",
                "市净率": stock.pbnewmrq or "",
                "行业": stock.industry or "",
            })
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "excel":
            filename = f"选股数据_{timestamp}.xlsx"
            return generate_excel(export_data, filename)
        else:
            filename = f"选股数据_{timestamp}.csv"
            return generate_csv(export_data, filename)
            
    except Exception as e:
        logger.error(f"导出选股数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/buy-signals", summary="导出买入信号", description="导出当前买入信号股票")
async def export_buy_signals(
    format: str = Query("csv", description="导出格式: csv 或 excel"),
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD")
):
    """导出买入信号数据"""
    from src.repositories.selection_repo import SelectionRepository
    
    try:
        repo = SelectionRepository()
        
        if date:
            query_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            query_date = datetime.now().date()
        
        stocks = repo.get_by_date(query_date)
        
        export_data = []
        for stock in stocks:
            signal_count = 0
            if getattr(stock, 'macd_golden_fork', None) == '1':
                signal_count += 1
            if getattr(stock, 'kdj_golden_fork', None) == '1':
                signal_count += 1
            if getattr(stock, 'break_through', None) == '1':
                signal_count += 1
            if getattr(stock, 'low_funds_inflow', None) == '1':
                signal_count += 1
            
            export_data.append({
                "代码": stock.code,
                "名称": stock.name,
                "信号数量": signal_count,
                "最新价": stock.new_price or "",
                "涨跌幅": stock.pct_chg or "",
                "成交量": stock.volume or "",
                "成交额": stock.amount or "",
                "行业": stock.industry or "",
            })
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "excel":
            filename = f"买入信号_{timestamp}.xlsx"
            return generate_excel(export_data, filename)
        else:
            filename = f"买入信号_{timestamp}.csv"
            return generate_csv(export_data, filename)
            
    except Exception as e:
        logger.error(f"导出买入信号失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")


@router.get("/sell-signals", summary="导出卖出信号", description="导出当前卖出信号股票")
async def export_sell_signals(
    format: str = Query("csv", description="导出格式: csv 或 excel"),
    date: Optional[str] = Query(None, description="日期 YYYY-MM-DD")
):
    """导出卖出信号数据"""
    from src.repositories.selection_repo import SelectionRepository
    
    try:
        repo = SelectionRepository()
        
        if date:
            query_date = datetime.strptime(date, "%Y-%m-%d").date()
        else:
            query_date = datetime.now().date()
        
        stocks = repo.get_by_date(query_date)
        
        export_data = []
        for stock in stocks:
            signal_count = 0
            if getattr(stock, 'macd_dead_fork', None) == '1':
                signal_count += 1
            if getattr(stock, 'kdj_dead_fork', None) == '1':
                signal_count += 1
            if getattr(stock, 'high_funds_outflow', None) == '1':
                signal_count += 1
            
            export_data.append({
                "代码": stock.code,
                "名称": stock.name,
                "信号数量": signal_count,
                "最新价": stock.new_price or "",
                "涨跌幅": stock.pct_chg or "",
                "成交量": stock.volume or "",
                "成交额": stock.amount or "",
                "行业": stock.industry or "",
            })
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "excel":
            filename = f"卖出信号_{timestamp}.xlsx"
            return generate_excel(export_data, filename)
        else:
            filename = f"卖出信号_{timestamp}.csv"
            return generate_csv(export_data, filename)
            
    except Exception as e:
        logger.error(f"导出卖出信号失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")
