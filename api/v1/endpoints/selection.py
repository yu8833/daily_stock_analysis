# -*- coding: utf-8 -*-
"""
===================================
选股数据接口
===================================

职责：
1. GET /api/v1/select 获取选股数据
2. 支持筛选、分页、排序
"""

import logging
from datetime import date as DateType, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.v1.schemas.common import ErrorResponse
from src.repositories.selection_repo import SelectionRepository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    responses={
        200: {"description": "选股数据"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取选股数据",
    description="获取综合选股数据，支持按行业、概念、基本面指标筛选"
)
def get_selection_data(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort_field: str = Query("change_rate", description="排序字段：change_rate/volume/deal_amount/pe/pb/turnoverrate/roe/sale_gpr/netprofit_yoy_ratio"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    keyword: Optional[str] = Query(None, description="关键字搜索，匹配代码/名称"),
    industries: Optional[list[str]] = Query(None, description="行业筛选（支持多选）"),
    concepts: Optional[list[str]] = Query(None, description="概念筛选（支持多选）"),
    areas: Optional[list[str]] = Query(None, description="地区筛选（支持多选）"),
    min_pe: Optional[float] = Query(None, description="最小市盈率"),
    max_pe: Optional[float] = Query(None, description="最大市盈率"),
    min_pb: Optional[float] = Query(None, description="最小市净率"),
    max_pb: Optional[float] = Query(None, description="最大市净率"),
    min_roe: Optional[float] = Query(None, description="最小ROE"),
    max_roe: Optional[float] = Query(None, description="最大ROE"),
    min_gpr: Optional[float] = Query(None, description="最小毛利率"),
    max_gpr: Optional[float] = Query(None, description="最大毛利率"),
    min_change: Optional[float] = Query(None, description="最小涨跌幅"),
    max_change: Optional[float] = Query(None, description="最大涨跌幅"),
    min_market_cap: Optional[float] = Query(None, description="最小市值（亿）"),
    max_market_cap: Optional[float] = Query(None, description="最大市值（亿）"),
    is_hs300: Optional[bool] = Query(None, description="是否沪深300成分股"),
    is_sz50: Optional[bool] = Query(None, description="是否上证50成分股"),
):
    """
    获取选股数据
    
    获取东方财富网选股器数据，支持多维度筛选和分页
    
    Args:
        date: 日期（YYYY-MM-DD），默认当天
        page: 页码，从1开始
        page_size: 每页条数，最大100条
        sort_field: 排序字段，支持 change_rate/volume/deal_amount/pe/pb/turnoverrate
        sort_order: 排序方式，asc（升序）或 desc（降序）
        keyword: 关键字搜索，匹配代码/名称
        industry: 行业筛选
        concept: 概念筛选
        min_pe: 最小市盈率
        max_pe: 最大市盈率
        min_pb: 最小市净率
        max_pb: 最大市净率
        min_change: 最小涨跌幅
        max_change: 最大涨跌幅
    
    Returns:
        包含日期、分页信息和股票列表的字典
    
    Raises:
        HTTPException: 500 - 获取数据失败
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

        results = repo.get_or_fetch(query_date)

        if industries:
            industry_set = set([i.lower().strip() for i in industries if i.strip()])
            if industry_set:
                results = [r for r in results if r.industry and any(ind in str(r.industry).lower() for ind in industry_set)]
        
        if concepts:
            concept_set = set([c.lower().strip() for c in concepts if c.strip()])
            if concept_set:
                results = [r for r in results if r.concept and any(con in str(r.concept).lower() for con in concept_set)]
        
        if areas:
            area_set = set([a.lower().strip() for a in areas if a.strip()])
            if area_set:
                results = [r for r in results if r.area and any(ar in str(r.area).lower() for ar in area_set)]
        
        if min_pe is not None:
            results = [r for r in results if r.pe is not None and r.pe >= min_pe]
        
        if max_pe is not None:
            results = [r for r in results if r.pe is not None and r.pe <= max_pe]
        
        if min_pb is not None:
            results = [r for r in results if r.pbnewmrq is not None and r.pbnewmrq >= min_pb]

        if max_pb is not None:
            results = [r for r in results if r.pbnewmrq is not None and r.pbnewmrq <= max_pb]
        
        if min_roe is not None:
            results = [r for r in results if r.roe_weight is not None and r.roe_weight >= min_roe]

        if max_roe is not None:
            results = [r for r in results if r.roe_weight is not None and r.roe_weight <= max_roe]
        
        if min_gpr is not None:
            results = [r for r in results if r.sale_gpr is not None and r.sale_gpr >= min_gpr]
        
        if max_gpr is not None:
            results = [r for r in results if r.sale_gpr is not None and r.sale_gpr <= max_gpr]
        
        if min_change is not None:
            results = [r for r in results if r.change_rate is not None and r.change_rate >= min_change]
        
        if max_change is not None:
            results = [r for r in results if r.change_rate is not None and r.change_rate <= max_change]
        
        if min_market_cap is not None:
            results = [r for r in results if r.total_market_cap is not None and r.total_market_cap >= min_market_cap * 100000000]
        
        if max_market_cap is not None:
            results = [r for r in results if r.total_market_cap is not None and r.total_market_cap <= max_market_cap * 100000000]
        
        if is_hs300 is not None:
            results = [r for r in results if str(r.is_hs300).strip() == ('Y' if is_hs300 else 'N')]
        
        if is_sz50 is not None:
            results = [r for r in results if str(r.is_sz50).strip() == ('Y' if is_sz50 else 'N')]
        
        if keyword:
            keyword_lower = keyword.lower().strip()
            filtered_results = []
            for item in results:
                code = str(item.code or '').lower()
                name = str(item.name or '').lower()
                industry = str(item.industry or '').lower()
                concept = str(item.concept or '').lower()
                area = str(item.area or '').lower()
                if (keyword_lower in code or
                    keyword_lower in name or
                    keyword_lower in industry or
                    keyword_lower in concept or
                    keyword_lower in area):
                    filtered_results.append(item)
            results = filtered_results

        # 字段映射：键为前端排序字段，值为数据模型字段
        field_mapping = {
            # 基本信息
            'code': 'code',
            'name': 'name',
            
            # 行情数据
            'change_rate': 'change_rate',
            'new_price': 'new_price',
            'volume_ratio': 'volume_ratio',
            'high_price': 'high_price',
            'low_price': 'low_price',
            'pre_close_price': 'pre_close_price',
            'volume': 'volume',
            'deal_amount': 'deal_amount',
            'turnoverrate': 'turnoverrate',
            'amplitude': 'amplitude',
            
            # 行业地区概念
            'industry': 'industry',
            'area': 'area',
            'concept': 'concept',
            
            # 估值指标
            'pe': 'pe',
            'pe9': 'pe9',
            'pbnewmrq': 'pbnewmrq',
            'pettmdeducted': 'pettmdeducted',
            'ps9': 'ps9',
            'pcfjyxjl9': 'pcfjyxjl9',
            'predict_pe_syear': 'predict_pe_syear',
            'predict_pe_nyear': 'predict_pe_nyear',
            'dtsyl': 'dtsyl',
            'ycpeg': 'ycpeg',
            'enterprise_value_multiple': 'enterprise_value_multiple',
            
            # 市值数据
            'total_market_cap': 'total_market_cap',
            'free_cap': 'free_cap',
            
            # 每股指标
            'basic_eps': 'basic_eps',
            'bvps': 'bvps',
            'per_netcash_operate': 'per_netcash_operate',
            'per_fcfe': 'per_fcfe',
            'per_capital_reserve': 'per_capital_reserve',
            'per_unassign_profit': 'per_unassign_profit',
            'per_surplus_reserve': 'per_surplus_reserve',
            'per_retained_earning': 'per_retained_earning',
            
            # 财务指标
            'parent_netprofit': 'parent_netprofit',
            'deduct_netprofit': 'deduct_netprofit',
            'total_operate_income': 'total_operate_income',
            'roe_weight': 'roe_weight',
            'jroa': 'jroa',
            'roic': 'roic',
            'zxgxl': 'zxgxl',
            'sale_gpr': 'sale_gpr',
            'sale_npr': 'sale_npr',
            
            # 增长率指标
            'netprofit_yoy_ratio': 'netprofit_yoy_ratio',
            'deduct_netprofit_growthrate': 'deduct_netprofit_growthrate',
            'toi_yoy_ratio': 'toi_yoy_ratio',
            'netprofit_growthrate_3y': 'netprofit_growthrate_3y',
            'income_growthrate_3y': 'income_growthrate_3y',
            'predict_netprofit_ratio': 'predict_netprofit_ratio',
            'predict_income_ratio': 'predict_income_ratio',
            'basiceps_yoy_ratio': 'basiceps_yoy_ratio',
            'total_profit_growthrate': 'total_profit_growthrate',
            'operate_profit_growthrate': 'operate_profit_growthrate',
            
            # 偿债能力
            'debt_asset_ratio': 'debt_asset_ratio',
            'equity_ratio': 'equity_ratio',
            'equity_multiplier': 'equity_multiplier',
            'current_ratio': 'current_ratio',
            'speed_ratio': 'speed_ratio',
            
            # 股本结构
            'total_shares': 'total_shares',
            'free_shares': 'free_shares',
            
            # 股东信息
            'holder_newest': 'holder_newest',
            'holder_ratio': 'holder_ratio',
            'hold_amount': 'hold_amount',
            'avg_hold_num': 'avg_hold_num',
            'holdnum_growthrate_3q': 'holdnum_growthrate_3q',
            'holdnum_growthrate_hy': 'holdnum_growthrate_hy',
            'hold_ratio_count': 'hold_ratio_count',
            'free_hold_ratio': 'free_hold_ratio',
            
            # 质押相关
            'pledge_ratio': 'pledge_ratio',
            'goodwill_scale': 'goodwill_scale',
            'goodwill_assets_ratro': 'goodwill_assets_ratro',
            
            # 分红相关
            'par_dividend_pretax': 'par_dividend_pretax',
            'par_dividend': 'par_dividend',
            'par_it_equity': 'par_it_equity',
            
            # 股东/高管变动
            'holder_change_3m': 'holder_change_3m',
            'executive_change_3m': 'executive_change_3m',
            'org_survey_3m': 'org_survey_3m',
            
            # 机构持股
            'allcorp_num': 'allcorp_num',
            'allcorp_fund_num': 'allcorp_fund_num',
            'allcorp_qs_num': 'allcorp_qs_num',
            'allcorp_qfii_num': 'allcorp_qfii_num',
            'allcorp_bx_num': 'allcorp_bx_num',
            'allcorp_sb_num': 'allcorp_sb_num',
            'allcorp_xt_num': 'allcorp_xt_num',
            'allcorp_ratio': 'allcorp_ratio',
            'allcorp_fund_ratio': 'allcorp_fund_ratio',
            'allcorp_qs_ratio': 'allcorp_qs_ratio',
            'allcorp_qfii_ratio': 'allcorp_qfii_ratio',
            'allcorp_bx_ratio': 'allcorp_bx_ratio',
            'allcorp_sb_ratio': 'allcorp_sb_ratio',
            'allcorp_xt_ratio': 'allcorp_xt_ratio',
            
            # 人气数据
            'popularity_rank': 'popularity_rank',
            'rank_change': 'rank_change',
            'upp_days': 'upp_days',
            'down_days': 'down_days',
            'new_high': 'new_high',
            'new_down': 'new_down',
            'newfans_ratio': 'newfans_ratio',
            'bigfans_ratio': 'bigfans_ratio',
            'concern_rank_7days': 'concern_rank_7days',
            'browse_rank': 'browse_rank',
            
            # 资金流向
            'net_inflow': 'net_inflow',
            'netinflow_3days': 'netinflow_3days',
            'netinflow_5days': 'netinflow_5days',
            'nowinterst_ratio': 'nowinterst_ratio',
            'nowinterst_ratio_3d': 'nowinterst_ratio_3d',
            'nowinterst_ratio_5d': 'nowinterst_ratio_5d',
            'ddx': 'ddx',
            'ddx_3d': 'ddx_3d',
            'ddx_5d': 'ddx_5d',
            'ddx_red_10d': 'ddx_red_10d',
            
            # 阶段涨跌幅
            'changerate_3days': 'changerate_3days',
            'changerate_5days': 'changerate_5days',
            'changerate_10days': 'changerate_10days',
            'changerate_ty': 'changerate_ty',
            'upnday': 'upnday',
            'downnday': 'downnday',
            
            # 上市数据
            'listing_yield_year': 'listing_yield_year',
            'listing_volatility_year': 'listing_volatility_year',
            
            # 沪深股通
            'mutual_netbuy_amt': 'mutual_netbuy_amt',
            'hold_ratio': 'hold_ratio',
        }
        
        # 验证排序字段
        if sort_field not in field_mapping:
            sort_field = 'change_rate'
        
        # 排序
        sort_key = field_mapping[sort_field]
        reverse = sort_order.lower() == 'desc'
        
        # 使用与limitup一致的排序逻辑
        results.sort(key=lambda x: (getattr(x, sort_key) or 0), reverse=reverse)
        
        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        formatted_data = []
        for item in paginated_results:
            formatted_data.append({
                # 基本信息
                "code": str(item.code).strip(),
                "name": str(item.name).strip(),
                
                # 行情数据
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
                
                # 行业地区概念
                "industry": str(item.industry).strip() if item.industry else None,
                "area": str(item.area).strip() if item.area else None,
                "concept": str(item.concept).strip() if item.concept else None,
                "style": str(item.style).strip() if item.style else None,
                
                # 指数成分
                "is_hs300": str(item.is_hs300).strip() if item.is_hs300 else None,
                "is_sz50": str(item.is_sz50).strip() if item.is_sz50 else None,
                "is_zz500": str(item.is_zz500).strip() if item.is_zz500 else None,
                "is_zz1000": str(item.is_zz1000).strip() if item.is_zz1000 else None,
                "is_cy50": str(item.is_cy50).strip() if item.is_cy50 else None,
                
                # 估值指标
                "pe": item.pe,
                "pe9": item.pe9,
                "pbnewmrq": item.pbnewmrq,
                "pettmdeducted": item.pettmdeducted,
                "ps9": item.ps9,
                "pcfjyxjl9": item.pcfjyxjl9,
                "predict_pe_syear": item.predict_pe_syear,
                "predict_pe_nyear": item.predict_pe_nyear,
                "dtsyl": item.dtsyl,
                "ycpeg": item.ycpeg,
                "enterprise_value_multiple": item.enterprise_value_multiple,
                
                # 市值数据
                "total_market_cap": item.total_market_cap,
                "free_cap": item.free_cap,
                
                # 每股指标
                "basic_eps": item.basic_eps,
                "bvps": item.bvps,
                "per_netcash_operate": item.per_netcash_operate,
                "per_fcfe": item.per_fcfe,
                "per_capital_reserve": item.per_capital_reserve,
                "per_unassign_profit": item.per_unassign_profit,
                "per_surplus_reserve": item.per_surplus_reserve,
                "per_retained_earning": item.per_retained_earning,
                
                # 财务指标
                "parent_netprofit": item.parent_netprofit,
                "deduct_netprofit": item.deduct_netprofit,
                "total_operate_income": item.total_operate_income,
                "roe_weight": item.roe_weight,
                "jroa": item.jroa,
                "roic": item.roic,
                "zxgxl": item.zxgxl,
                "sale_gpr": item.sale_gpr,
                "sale_npr": item.sale_npr,
                
                # 增长率指标
                "netprofit_yoy_ratio": item.netprofit_yoy_ratio,
                "deduct_netprofit_growthrate": item.deduct_netprofit_growthrate,
                "toi_yoy_ratio": item.toi_yoy_ratio,
                "netprofit_growthrate_3y": item.netprofit_growthrate_3y,
                "income_growthrate_3y": item.income_growthrate_3y,
                "predict_netprofit_ratio": item.predict_netprofit_ratio,
                "predict_income_ratio": item.predict_income_ratio,
                "basiceps_yoy_ratio": item.basiceps_yoy_ratio,
                "total_profit_growthrate": item.total_profit_growthrate,
                "operate_profit_growthrate": item.operate_profit_growthrate,
                
                # 偿债能力
                "debt_asset_ratio": item.debt_asset_ratio,
                "equity_ratio": item.equity_ratio,
                "equity_multiplier": item.equity_multiplier,
                "current_ratio": item.current_ratio,
                "speed_ratio": item.speed_ratio,
                
                # 股本结构
                "total_shares": item.total_shares,
                "free_shares": item.free_shares,
                
                # 股东信息
                "holder_newest": item.holder_newest,
                "holder_ratio": item.holder_ratio,
                "hold_amount": item.hold_amount,
                "avg_hold_num": item.avg_hold_num,
                "holdnum_growthrate_3q": item.holdnum_growthrate_3q,
                "holdnum_growthrate_hy": item.holdnum_growthrate_hy,
                "hold_ratio_count": item.hold_ratio_count,
                "free_hold_ratio": item.free_hold_ratio,
                
                # 技术指标信号
                "macd_golden_fork": str(item.macd_golden_fork).strip() if item.macd_golden_fork else None,
                "macd_golden_forkz": str(item.macd_golden_forkz).strip() if item.macd_golden_forkz else None,
                "macd_golden_forky": str(item.macd_golden_forky).strip() if item.macd_golden_forky else None,
                "kdj_golden_fork": str(item.kdj_golden_fork).strip() if item.kdj_golden_fork else None,
                "kdj_golden_forkz": str(item.kdj_golden_forkz).strip() if item.kdj_golden_forkz else None,
                "kdj_golden_forky": str(item.kdj_golden_forky).strip() if item.kdj_golden_forky else None,
                
                # 突破信号
                "break_through": str(item.break_through).strip() if item.break_through else None,
                "low_funds_inflow": str(item.low_funds_inflow).strip() if item.low_funds_inflow else None,
                "high_funds_outflow": str(item.high_funds_outflow).strip() if item.high_funds_outflow else None,
                "breakup_ma_5days": str(item.breakup_ma_5days).strip() if item.breakup_ma_5days else None,
                "breakup_ma_10days": str(item.breakup_ma_10days).strip() if item.breakup_ma_10days else None,
                "breakup_ma_20days": str(item.breakup_ma_20days).strip() if item.breakup_ma_20days else None,
                "breakup_ma_30days": str(item.breakup_ma_30days).strip() if item.breakup_ma_30days else None,
                "breakup_ma_60days": str(item.breakup_ma_60days).strip() if item.breakup_ma_60days else None,
                
                # 均线排列
                "long_avg_array": str(item.long_avg_array).strip() if item.long_avg_array else None,
                "short_avg_array": str(item.short_avg_array).strip() if item.short_avg_array else None,
                
                # 量价关系
                "upper_large_volume": str(item.upper_large_volume).strip() if item.upper_large_volume else None,
                "down_narrow_volume": str(item.down_narrow_volume).strip() if item.down_narrow_volume else None,
                
                # K线形态
                "one_dayang_line": str(item.one_dayang_line).strip() if item.one_dayang_line else None,
                "two_dayang_lines": str(item.two_dayang_lines).strip() if item.two_dayang_lines else None,
                "rise_sun": str(item.rise_sun).strip() if item.rise_sun else None,
                "power_fulgun": str(item.power_fulgun).strip() if item.power_fulgun else None,
                "restore_justice": str(item.restore_justice).strip() if item.restore_justice else None,
                "down_7days": str(item.down_7days).strip() if item.down_7days else None,
                "upper_8days": str(item.upper_8days).strip() if item.upper_8days else None,
                "upper_9days": str(item.upper_9days).strip() if item.upper_9days else None,
                "upper_4days": str(item.upper_4days).strip() if item.upper_4days else None,
                "heaven_rule": str(item.heaven_rule).strip() if item.heaven_rule else None,
                "upside_volume": str(item.upside_volume).strip() if item.upside_volume else None,
                "bearish_engulfing": str(item.bearish_engulfing).strip() if item.bearish_engulfing else None,
                "reversing_hammer": str(item.reversing_hammer).strip() if item.reversing_hammer else None,
                "shooting_star": str(item.shooting_star).strip() if item.shooting_star else None,
                "evening_star": str(item.evening_star).strip() if item.evening_star else None,
                "first_dawn": str(item.first_dawn).strip() if item.first_dawn else None,
                "pregnant": str(item.pregnant).strip() if item.pregnant else None,
                "black_cloud_tops": str(item.black_cloud_tops).strip() if item.black_cloud_tops else None,
                "morning_star": str(item.morning_star).strip() if item.morning_star else None,
                "narrow_finish": str(item.narrow_finish).strip() if item.narrow_finish else None,
                
                # 涨跌停统计
                "limited_lift_f6m": item.limited_lift_f6m,
                "limited_lift_f1y": item.limited_lift_f1y,
                "limited_lift_6m": item.limited_lift_6m,
                "limited_lift_1y": item.limited_lift_1y,
                
                # 阶段涨跌幅
                "directional_seo_1m": item.directional_seo_1m,
                "directional_seo_3m": item.directional_seo_3m,
                
                # 均线数据
                "ma5": item.ma5,
                "ma10": item.ma10,
                "ma20": item.ma20,
                "ma60": item.ma60,
                "ma120": item.ma120,
                "ma250": item.ma250,
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
        logger.error(f"获取选股数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取选股数据失败: {str(e)}"
            }
        )


@router.get(
    "/industries",
    responses={
        200: {"description": "行业列表"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取行业列表",
    description="获取选股数据中的所有行业列表"
)
def get_industries(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    获取行业列表
    
    Args:
        date: 日期（YYYY-MM-DD），默认当天
    
    Returns:
        行业名称列表
    
    Raises:
        HTTPException: 500 - 获取数据失败
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
        
        industries = repo.get_all_industries(query_date)
        
        return {
            "date": query_date.isoformat(),
            "industries": sorted(industries)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取行业列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取行业列表失败: {str(e)}"
            }
        )


@router.get(
    "/concepts",
    responses={
        200: {"description": "概念列表"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取概念列表",
    description="获取选股数据中的所有概念列表"
)
def get_concepts(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
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
        
        concepts = repo.get_all_concepts(query_date)
        
        return {
            "date": query_date.isoformat(),
            "concepts": sorted(concepts)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取概念列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取概念列表失败: {str(e)}"
            }
        )


@router.get(
    "/areas",
    responses={
        200: {"description": "地区列表"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="获取地区列表",
    description="获取选股数据中的所有地区列表"
)
def get_areas(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
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
        
        areas = repo.get_all_areas(query_date)
        
        return {
            "date": query_date.isoformat(),
            "areas": sorted(areas)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取地区列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取地区列表失败: {str(e)}"
            }
        )


@router.post(
    "/fetch",
    responses={
        200: {"description": "数据获取成功"},
        500: {"description": "服务器错误", "model": ErrorResponse},
    },
    summary="手动触发获取选股数据",
    description="手动触发从东方财富网获取选股数据并保存到数据库"
)
def fetch_selection_data(
    date: Optional[str] = Query(None, description="日期（YYYY-MM-DD），默认当天")
):
    """
    手动触发获取选股数据
    
    从东方财富网获取选股数据并保存到数据库
    
    Args:
        date: 日期（YYYY-MM-DD），默认当天
    
    Returns:
        保存的记录数
    
    Raises:
        HTTPException: 500 - 获取数据失败
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
        
        count = repo.save_from_fetcher(query_date)
        
        return {
            "date": query_date.isoformat(),
            "saved_count": count,
            "message": f"成功获取并保存 {count} 条选股数据"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"手动获取选股数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"获取选股数据失败: {str(e)}"
            }
        )
