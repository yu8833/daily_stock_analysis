# -*- coding: utf-8 -*-
"""
===================================
选股数据访问层
===================================

职责：
1. 封装选股数据的数据库操作
2. 提供选股数据查询接口
3. 支持数据持久化和缓存
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any

import pandas as pd
from sqlalchemy import select, and_, desc, delete

from src.storage import DatabaseManager, StockSelection
from data_provider.eastmoney_selection_fetcher import EastmoneySelectionFetcher

logger = logging.getLogger(__name__)


class SelectionRepository:
    """
    选股数据访问层
    
    封装 StockSelection 表的数据库操作，支持从数据源获取并持久化
    """
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        初始化数据访问层
        
        Args:
            db_manager: 数据库管理器（可选，默认使用单例）
        """
        self.db = db_manager or DatabaseManager.get_instance()
        self.fetcher = EastmoneySelectionFetcher()
    
    def get_by_date(self, query_date: date) -> List[StockSelection]:
        """
        获取指定日期的选股数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            StockSelection 对象列表
        """
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection)
                .where(StockSelection.date == query_date)
                .order_by(desc(StockSelection.change_rate), StockSelection.code)
            ).scalars().all()
            return list(results)
    
    def get_by_code(self, code: str, days: int = 30) -> List[StockSelection]:
        """
        获取指定股票的选股历史
        
        Args:
            code: 股票代码
            days: 最近天数
            
        Returns:
            StockSelection 对象列表
        """
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection)
                .where(and_(
                    StockSelection.code == code,
                    StockSelection.date >= cutoff_date.date()
                ))
                .order_by(desc(StockSelection.date))
            ).scalars().all()
            return list(results)
    
    def get_by_industry(self, industry: str, query_date: Optional[date] = None) -> List[StockSelection]:
        """
        获取指定行业的选股数据
        
        Args:
            industry: 行业名称
            query_date: 查询日期（默认当天）
            
        Returns:
            StockSelection 对象列表
        """
        if query_date is None:
            query_date = date.today()
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection)
                .where(and_(
                    StockSelection.date == query_date,
                    StockSelection.industry.like(f"%{industry}%")
                ))
                .order_by(desc(StockSelection.change_rate))
            ).scalars().all()
            return list(results)
    
    def has_date_data(self, query_date: date) -> bool:
        """
        检查指定日期是否已有数据
        
        Args:
            query_date: 查询日期
            
        Returns:
            是否存在数据
        """
        with self.db.get_session() as session:
            result = session.execute(
                select(StockSelection)
                .where(StockSelection.date == query_date)
            ).scalar_one_or_none()
            return result is not None
    
    def save_from_fetcher(self, query_date: date) -> int:
        """
        从数据源获取数据并保存到数据库
        
        Args:
            query_date: 查询日期
            
        Returns:
            保存的记录数
        """
        df = self.fetcher.fetch_selection_data()
        
        if df is None or df.empty:
            logger.info(f"未获取到 {query_date} 的选股数据")
            return 0
        
        self._delete_date_data(query_date)
        
        saved_count = 0
        with self.db.get_session() as session:
            for _, row in df.iterrows():
                try:
                    record = StockSelection(
                        date=query_date,
                        code=str(row.get('code', '')).strip(),
                        name=str(row.get('name', '')).strip(),
                        
                        # 行情数据
                        new_price=row.get('new_price'),
                        change_rate=row.get('change_rate'),
                        volume_ratio=row.get('volume_ratio'),
                        high_price=row.get('high_price'),
                        low_price=row.get('low_price'),
                        pre_close_price=row.get('pre_close_price'),
                        volume=row.get('volume'),
                        deal_amount=row.get('deal_amount'),
                        turnoverrate=row.get('turnoverrate'),
                        amplitude=row.get('amplitude'),
                        listing_date=row.get('listing_date'),
                        
                        # 行业地区概念
                        industry=str(row.get('industry', '')).strip() if pd.notna(row.get('industry')) else None,
                        area=str(row.get('area', '')).strip() if pd.notna(row.get('area')) else None,
                        concept=str(row.get('concept', '')).strip() if pd.notna(row.get('concept')) else None,
                        style=str(row.get('style', '')).strip() if pd.notna(row.get('style')) else None,
                        
                        # 指数成分
                        is_hs300=str(row.get('is_hs300', '')).strip() if pd.notna(row.get('is_hs300')) else None,
                        is_sz50=str(row.get('is_sz50', '')).strip() if pd.notna(row.get('is_sz50')) else None,
                        is_zz500=str(row.get('is_zz500', '')).strip() if pd.notna(row.get('is_zz500')) else None,
                        is_zz1000=str(row.get('is_zz1000', '')).strip() if pd.notna(row.get('is_zz1000')) else None,
                        is_cy50=str(row.get('is_cy50', '')).strip() if pd.notna(row.get('is_cy50')) else None,
                        
                        # 估值指标
                        pe=row.get('pe'),
                        pe9=row.get('pe9'),
                        pbnewmrq=row.get('pbnewmrq'),
                        pettmdeducted=row.get('pettmdeducted'),
                        ps9=row.get('ps9'),
                        pcfjyxjl9=row.get('pcfjyxjl9'),
                        predict_pe_syear=row.get('predict_pe_syear'),
                        predict_pe_nyear=row.get('predict_pe_nyear'),
                        dtsyl=row.get('dtsyl'),
                        ycpeg=row.get('ycpeg'),
                        enterprise_value_multiple=row.get('enterprise_value_multiple'),
                        
                        # 市值数据
                        total_market_cap=row.get('total_market_cap'),
                        free_cap=row.get('free_cap'),
                        
                        # 每股指标
                        basic_eps=row.get('basic_eps'),
                        bvps=row.get('bvps'),
                        per_netcash_operate=row.get('per_netcash_operate'),
                        per_fcfe=row.get('per_fcfe'),
                        per_capital_reserve=row.get('per_capital_reserve'),
                        per_unassign_profit=row.get('per_unassign_profit'),
                        per_surplus_reserve=row.get('per_surplus_reserve'),
                        per_retained_earning=row.get('per_retained_earning'),
                        
                        # 财务指标
                        parent_netprofit=row.get('parent_netprofit'),
                        deduct_netprofit=row.get('deduct_netprofit'),
                        total_operate_income=row.get('total_operate_income'),
                        roe_weight=row.get('roe_weight'),
                        jroa=row.get('jroa'),
                        roic=row.get('roic'),
                        zxgxl=row.get('zxgxl'),
                        sale_gpr=row.get('sale_gpr'),
                        sale_npr=row.get('sale_npr'),
                        
                        # 增长率指标
                        netprofit_yoy_ratio=row.get('netprofit_yoy_ratio'),
                        deduct_netprofit_growthrate=row.get('deduct_netprofit_growthrate'),
                        toi_yoy_ratio=row.get('toi_yoy_ratio'),
                        netprofit_growthrate_3y=row.get('netprofit_growthrate_3y'),
                        income_growthrate_3y=row.get('income_growthrate_3y'),
                        predict_netprofit_ratio=row.get('predict_netprofit_ratio'),
                        predict_income_ratio=row.get('predict_income_ratio'),
                        basiceps_yoy_ratio=row.get('basiceps_yoy_ratio'),
                        total_profit_growthrate=row.get('total_profit_growthrate'),
                        operate_profit_growthrate=row.get('operate_profit_growthrate'),
                        
                        # 偿债能力
                        debt_asset_ratio=row.get('debt_asset_ratio'),
                        equity_ratio=row.get('equity_ratio'),
                        equity_multiplier=row.get('equity_multiplier'),
                        current_ratio=row.get('current_ratio'),
                        speed_ratio=row.get('speed_ratio'),
                        
                        # 股本结构
                        total_shares=row.get('total_shares'),
                        free_shares=row.get('free_shares'),
                        
                        # 股东信息
                        holder_newest=row.get('holder_newest'),
                        holder_ratio=row.get('holder_ratio'),
                        hold_amount=row.get('hold_amount'),
                        avg_hold_num=row.get('avg_hold_num'),
                        holdnum_growthrate_3q=row.get('holdnum_growthrate_3q'),
                        holdnum_growthrate_hy=row.get('holdnum_growthrate_hy'),
                        hold_ratio_count=row.get('hold_ratio_count'),
                        free_hold_ratio=row.get('free_hold_ratio'),
                        
                        # 技术指标信号
                        macd_golden_fork=str(row.get('macd_golden_fork', '')).strip() if pd.notna(row.get('macd_golden_fork')) else None,
                        macd_golden_forkz=str(row.get('macd_golden_forkz', '')).strip() if pd.notna(row.get('macd_golden_forkz')) else None,
                        macd_golden_forky=str(row.get('macd_golden_forky', '')).strip() if pd.notna(row.get('macd_golden_forky')) else None,
                        kdj_golden_fork=str(row.get('kdj_golden_fork', '')).strip() if pd.notna(row.get('kdj_golden_fork')) else None,
                        kdj_golden_forkz=str(row.get('kdj_golden_forkz', '')).strip() if pd.notna(row.get('kdj_golden_forkz')) else None,
                        kdj_golden_forky=str(row.get('kdj_golden_forky', '')).strip() if pd.notna(row.get('kdj_golden_forky')) else None,
                        
                        # 突破信号
                        break_through=str(row.get('break_through', '')).strip() if pd.notna(row.get('break_through')) else None,
                        low_funds_inflow=str(row.get('low_funds_inflow', '')).strip() if pd.notna(row.get('low_funds_inflow')) else None,
                        high_funds_outflow=str(row.get('high_funds_outflow', '')).strip() if pd.notna(row.get('high_funds_outflow')) else None,
                        breakup_ma_5days=str(row.get('breakup_ma_5days', '')).strip() if pd.notna(row.get('breakup_ma_5days')) else None,
                        breakup_ma_10days=str(row.get('breakup_ma_10days', '')).strip() if pd.notna(row.get('breakup_ma_10days')) else None,
                        breakup_ma_20days=str(row.get('breakup_ma_20days', '')).strip() if pd.notna(row.get('breakup_ma_20days')) else None,
                        breakup_ma_30days=str(row.get('breakup_ma_30days', '')).strip() if pd.notna(row.get('breakup_ma_30days')) else None,
                        breakup_ma_60days=str(row.get('breakup_ma_60days', '')).strip() if pd.notna(row.get('breakup_ma_60days')) else None,
                        
                        # 均线排列
                        long_avg_array=str(row.get('long_avg_array', '')).strip() if pd.notna(row.get('long_avg_array')) else None,
                        short_avg_array=str(row.get('short_avg_array', '')).strip() if pd.notna(row.get('short_avg_array')) else None,
                        
                        # 量价关系
                        upper_large_volume=str(row.get('upper_large_volume', '')).strip() if pd.notna(row.get('upper_large_volume')) else None,
                        down_narrow_volume=str(row.get('down_narrow_volume', '')).strip() if pd.notna(row.get('down_narrow_volume')) else None,
                        
                        # K线形态
                        one_dayang_line=str(row.get('one_dayang_line', '')).strip() if pd.notna(row.get('one_dayang_line')) else None,
                        two_dayang_lines=str(row.get('two_dayang_lines', '')).strip() if pd.notna(row.get('two_dayang_lines')) else None,
                        rise_sun=str(row.get('rise_sun', '')).strip() if pd.notna(row.get('rise_sun')) else None,
                        power_fulgun=str(row.get('power_fulgun', '')).strip() if pd.notna(row.get('power_fulgun')) else None,
                        restore_justice=str(row.get('restore_justice', '')).strip() if pd.notna(row.get('restore_justice')) else None,
                        down_7days=str(row.get('down_7days', '')).strip() if pd.notna(row.get('down_7days')) else None,
                        upper_8days=str(row.get('upper_8days', '')).strip() if pd.notna(row.get('upper_8days')) else None,
                        upper_9days=str(row.get('upper_9days', '')).strip() if pd.notna(row.get('upper_9days')) else None,
                        upper_4days=str(row.get('upper_4days', '')).strip() if pd.notna(row.get('upper_4days')) else None,
                        heaven_rule=str(row.get('heaven_rule', '')).strip() if pd.notna(row.get('heaven_rule')) else None,
                        upside_volume=str(row.get('upside_volume', '')).strip() if pd.notna(row.get('upside_volume')) else None,
                        bearish_engulfing=str(row.get('bearish_engulfing', '')).strip() if pd.notna(row.get('bearish_engulfing')) else None,
                        reversing_hammer=str(row.get('reversing_hammer', '')).strip() if pd.notna(row.get('reversing_hammer')) else None,
                        shooting_star=str(row.get('shooting_star', '')).strip() if pd.notna(row.get('shooting_star')) else None,
                        evening_star=str(row.get('evening_star', '')).strip() if pd.notna(row.get('evening_star')) else None,
                        first_dawn=str(row.get('first_dawn', '')).strip() if pd.notna(row.get('first_dawn')) else None,
                        pregnant=str(row.get('pregnant', '')).strip() if pd.notna(row.get('pregnant')) else None,
                        black_cloud_tops=str(row.get('black_cloud_tops', '')).strip() if pd.notna(row.get('black_cloud_tops')) else None,
                        morning_star=str(row.get('morning_star', '')).strip() if pd.notna(row.get('morning_star')) else None,
                        narrow_finish=str(row.get('narrow_finish', '')).strip() if pd.notna(row.get('narrow_finish')) else None,
                        
                        # 限售和事件相关
                        limited_lift_f6m=str(row.get('limited_lift_f6m', '')).strip() if pd.notna(row.get('limited_lift_f6m')) else None,
                        limited_lift_f1y=str(row.get('limited_lift_f1y', '')).strip() if pd.notna(row.get('limited_lift_f1y')) else None,
                        limited_lift_6m=str(row.get('limited_lift_6m', '')).strip() if pd.notna(row.get('limited_lift_6m')) else None,
                        limited_lift_1y=str(row.get('limited_lift_1y', '')).strip() if pd.notna(row.get('limited_lift_1y')) else None,
                        directional_seo_1m=str(row.get('directional_seo_1m', '')).strip() if pd.notna(row.get('directional_seo_1m')) else None,
                        directional_seo_3m=str(row.get('directional_seo_3m', '')).strip() if pd.notna(row.get('directional_seo_3m')) else None,
                        directional_seo_6m=str(row.get('directional_seo_6m', '')).strip() if pd.notna(row.get('directional_seo_6m')) else None,
                        directional_seo_1y=str(row.get('directional_seo_1y', '')).strip() if pd.notna(row.get('directional_seo_1y')) else None,
                        recapitalize_1m=str(row.get('recapitalize_1m', '')).strip() if pd.notna(row.get('recapitalize_1m')) else None,
                        recapitalize_3m=str(row.get('recapitalize_3m', '')).strip() if pd.notna(row.get('recapitalize_3m')) else None,
                        recapitalize_6m=str(row.get('recapitalize_6m', '')).strip() if pd.notna(row.get('recapitalize_6m')) else None,
                        recapitalize_1y=str(row.get('recapitalize_1y', '')).strip() if pd.notna(row.get('recapitalize_1y')) else None,
                        equity_pledge_1m=str(row.get('equity_pledge_1m', '')).strip() if pd.notna(row.get('equity_pledge_1m')) else None,
                        equity_pledge_3m=str(row.get('equity_pledge_3m', '')).strip() if pd.notna(row.get('equity_pledge_3m')) else None,
                        equity_pledge_6m=str(row.get('equity_pledge_6m', '')).strip() if pd.notna(row.get('equity_pledge_6m')) else None,
                        equity_pledge_1y=str(row.get('equity_pledge_1y', '')).strip() if pd.notna(row.get('equity_pledge_1y')) else None,
                        pledge_ratio=row.get('pledge_ratio'),
                        goodwill_scale=row.get('goodwill_scale'),
                        goodwill_assets_ratro=row.get('goodwill_assets_ratro'),
                        predict_type=str(row.get('predict_type', '')).strip() if pd.notna(row.get('predict_type')) else None,
                        par_dividend_pretax=row.get('par_dividend_pretax'),
                        par_dividend=row.get('par_dividend'),
                        par_it_equity=row.get('par_it_equity'),
                        holder_change_3m=row.get('holder_change_3m'),
                        executive_change_3m=row.get('executive_change_3m'),
                        org_survey_3m=row.get('org_survey_3m'),
                        org_rating=str(row.get('org_rating', '')).strip() if pd.notna(row.get('org_rating')) else None,
                        
                        # 机构持股
                        allcorp_num=row.get('allcorp_num'),
                        allcorp_fund_num=row.get('allcorp_fund_num'),
                        allcorp_qs_num=row.get('allcorp_qs_num'),
                        allcorp_qfii_num=row.get('allcorp_qfii_num'),
                        allcorp_bx_num=row.get('allcorp_bx_num'),
                        allcorp_sb_num=row.get('allcorp_sb_num'),
                        allcorp_xt_num=row.get('allcorp_xt_num'),
                        allcorp_ratio=row.get('allcorp_ratio'),
                        allcorp_fund_ratio=row.get('allcorp_fund_ratio'),
                        allcorp_qs_ratio=row.get('allcorp_qs_ratio'),
                        allcorp_qfii_ratio=row.get('allcorp_qfii_ratio'),
                        allcorp_bx_ratio=row.get('allcorp_bx_ratio'),
                        allcorp_sb_ratio=row.get('allcorp_sb_ratio'),
                        allcorp_xt_ratio=row.get('allcorp_xt_ratio'),
                        
                        # 人气排名
                        popularity_rank=row.get('popularity_rank'),
                        rank_change=row.get('rank_change'),
                        upp_days=row.get('upp_days'),
                        down_days=row.get('down_days'),
                        new_high=row.get('new_high'),
                        new_down=row.get('new_down'),
                        newfans_ratio=row.get('newfans_ratio'),
                        bigfans_ratio=row.get('bigfans_ratio'),
                        concern_rank_7days=row.get('concern_rank_7days'),
                        browse_rank=row.get('browse_rank'),
                        
                        # 破净和新高
                        is_issue_break=str(row.get('is_issue_break', '')).strip() if pd.notna(row.get('is_issue_break')) else None,
                        is_bps_break=str(row.get('is_bps_break', '')).strip() if pd.notna(row.get('is_bps_break')) else None,
                        now_newhigh=str(row.get('now_newhigh', '')).strip() if pd.notna(row.get('now_newhigh')) else None,
                        now_newlow=str(row.get('now_newlow', '')).strip() if pd.notna(row.get('now_newlow')) else None,
                        high_recent_3days=str(row.get('high_recent_3days', '')).strip() if pd.notna(row.get('high_recent_3days')) else None,
                        high_recent_5days=str(row.get('high_recent_5days', '')).strip() if pd.notna(row.get('high_recent_5days')) else None,
                        high_recent_10days=str(row.get('high_recent_10days', '')).strip() if pd.notna(row.get('high_recent_10days')) else None,
                        high_recent_20days=str(row.get('high_recent_20days', '')).strip() if pd.notna(row.get('high_recent_20days')) else None,
                        high_recent_30days=str(row.get('high_recent_30days', '')).strip() if pd.notna(row.get('high_recent_30days')) else None,
                        low_recent_3days=str(row.get('low_recent_3days', '')).strip() if pd.notna(row.get('low_recent_3days')) else None,
                        low_recent_5days=str(row.get('low_recent_5days', '')).strip() if pd.notna(row.get('low_recent_5days')) else None,
                        low_recent_10days=str(row.get('low_recent_10days', '')).strip() if pd.notna(row.get('low_recent_10days')) else None,
                        low_recent_20days=str(row.get('low_recent_20days', '')).strip() if pd.notna(row.get('low_recent_20days')) else None,
                        low_recent_30days=str(row.get('low_recent_30days', '')).strip() if pd.notna(row.get('low_recent_30days')) else None,
                        
                        # 跑赢大盘
                        win_market_3days=str(row.get('win_market_3days', '')).strip() if pd.notna(row.get('win_market_3days')) else None,
                        win_market_5days=str(row.get('win_market_5days', '')).strip() if pd.notna(row.get('win_market_5days')) else None,
                        win_market_10days=str(row.get('win_market_10days', '')).strip() if pd.notna(row.get('win_market_10days')) else None,
                        win_market_20days=str(row.get('win_market_20days', '')).strip() if pd.notna(row.get('win_market_20days')) else None,
                        win_market_30days=str(row.get('win_market_30days', '')).strip() if pd.notna(row.get('win_market_30days')) else None,
                        
                        # 资金流入
                        net_inflow=row.get('net_inflow'),
                        netinflow_3days=row.get('netinflow_3days'),
                        netinflow_5days=row.get('netinflow_5days'),
                        nowinterst_ratio=row.get('nowinterst_ratio'),
                        nowinterst_ratio_3d=row.get('nowinterst_ratio_3d'),
                        nowinterst_ratio_5d=row.get('nowinterst_ratio_5d'),
                        ddx=row.get('ddx'),
                        ddx_3d=row.get('ddx_3d'),
                        ddx_5d=row.get('ddx_5d'),
                        ddx_red_10d=row.get('ddx_red_10d'),
                        
                        # 涨跌幅和天数
                        changerate_3days=row.get('changerate_3days'),
                        changerate_5days=row.get('changerate_5days'),
                        changerate_10days=row.get('changerate_10days'),
                        changerate_ty=row.get('changerate_ty'),
                        upnday=row.get('upnday'),
                        downnday=row.get('downnday'),
                        
                        # 上市相关
                        listing_yield_year=row.get('listing_yield_year'),
                        listing_volatility_year=row.get('listing_volatility_year'),
                        
                        # 沪深股通
                        mutual_netbuy_amt=row.get('mutual_netbuy_amt'),
                        hold_ratio=row.get('hold_ratio'),
                        
                        # 均线数据
                        ma5=row.get('ma5'),
                        ma10=row.get('ma10'),
                        ma20=row.get('ma20'),
                        ma60=row.get('ma60'),
                        ma120=row.get('ma120'),
                        ma250=row.get('ma250'),
                    )
                    session.add(record)
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"保存选股数据失败 (code={row.get('code')}): {e}")
            
            session.commit()
            logger.info(f"保存选股数据成功: {query_date}, 新增 {saved_count} 条")
        
        return saved_count
    
    def _delete_date_data(self, query_date: date) -> None:
        """
        删除指定日期的数据
        
        Args:
            query_date: 查询日期
        """
        with self.db.get_session() as session:
            session.execute(
                delete(StockSelection)
                .where(StockSelection.date == query_date)
            )
            session.commit()
    
    def get_or_fetch(self, query_date: date) -> List[StockSelection]:
        """
        获取指定日期的选股数据，如果数据库中没有则从数据源获取并保存
        
        Args:
            query_date: 查询日期
            
        Returns:
            StockSelection 对象列表
        """
        results = self.get_by_date(query_date)
        if results:
            logger.debug(f"从数据库获取选股数据: {query_date}, {len(results)} 条")
            return results
        
        logger.info(f"数据库未找到 {query_date} 的选股数据，从数据源获取")
        self.save_from_fetcher(query_date)
        
        return self.get_by_date(query_date)
    
    def get_all_industries(self, query_date: Optional[date] = None) -> List[str]:
        """
        获取所有行业列表
        
        Args:
            query_date: 查询日期（默认当天）
            
        Returns:
            行业名称列表
        """
        if query_date is None:
            query_date = date.today()
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection.industry)
                .where(StockSelection.date == query_date)
                .distinct()
            ).scalars().all()
            return [str(i) for i in results if i]
    
    def get_all_concepts(self, query_date: Optional[date] = None) -> List[str]:
        """
        获取所有概念列表
        
        Args:
            query_date: 查询日期（默认当天）
            
        Returns:
            概念名称列表
        """
        if query_date is None:
            query_date = date.today()
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection.concept)
                .where(StockSelection.date == query_date)
                .distinct()
            ).scalars().all()
            return [str(c) for c in results if c]
    
    def get_all_areas(self, query_date: Optional[date] = None) -> List[str]:
        """
        获取所有地区列表
        
        Args:
            query_date: 查询日期（默认当天）
            
        Returns:
            地区名称列表
        """
        if query_date is None:
            query_date = date.today()
        
        with self.db.get_session() as session:
            results = session.execute(
                select(StockSelection.area)
                .where(StockSelection.date == query_date)
                .distinct()
            ).scalars().all()
            return [str(a) for a in results if a]
