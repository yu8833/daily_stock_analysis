# -*- coding: utf-8 -*-
"""
===================================
东方财富网选股器数据获取器
===================================

职责：
1. 从东方财富网获取选股器数据
2. 支持多页数据抓取
3. 数据标准化处理
"""

import logging
import math
import random
import time
from typing import Optional, List, Dict, Any

import pandas as pd
import requests

from data_provider.base import BaseFetcher

logger = logging.getLogger(__name__)


# 选股器字段映射 - 完整字段列表 (参考 instock)
SELECTION_COLUMNS = {
    # 基本信息
    'MAX_TRADE_DATE': {'name': 'date', 'cn': '日期'},
    'SECURITY_CODE': {'name': 'code', 'cn': '代码'},
    'SECURITY_NAME_ABBR': {'name': 'name', 'cn': '名称'},
    
    # 行情数据
    'NEW_PRICE': {'name': 'new_price', 'cn': '最新价'},
    'CHANGE_RATE': {'name': 'change_rate', 'cn': '涨跌幅'},
    'VOLUME_RATIO': {'name': 'volume_ratio', 'cn': '量比'},
    'HIGH_PRICE': {'name': 'high_price', 'cn': '最高价'},
    'LOW_PRICE': {'name': 'low_price', 'cn': '最低价'},
    'PRE_CLOSE_PRICE': {'name': 'pre_close_price', 'cn': '昨收价'},
    'VOLUME': {'name': 'volume', 'cn': '成交量'},
    'DEAL_AMOUNT': {'name': 'deal_amount', 'cn': '成交额'},
    'TURNOVERRATE': {'name': 'turnoverrate', 'cn': '换手率'},
    'AMPLITUDE': {'name': 'amplitude', 'cn': '振幅'},
    'LISTING_DATE': {'name': 'listing_date', 'cn': '上市时间'},
    
    # 行业地区概念
    'INDUSTRY': {'name': 'industry', 'cn': '行业'},
    'AREA': {'name': 'area', 'cn': '地区'},
    'CONCEPT': {'name': 'concept', 'cn': '概念'},
    'STYLE': {'name': 'style', 'cn': '风格'},
    
    # 指数成分
    'IS_HS300': {'name': 'is_hs300', 'cn': '沪深300'},
    'IS_SZ50': {'name': 'is_sz50', 'cn': '上证50'},
    'IS_ZZ500': {'name': 'is_zz500', 'cn': '中证500'},
    'IS_ZZ1000': {'name': 'is_zz1000', 'cn': '中证1000'},
    'IS_CY50': {'name': 'is_cy50', 'cn': '创业板50'},
    
    # 估值指标
    'PE': {'name': 'pe', 'cn': '市盈率'},
    'PE9': {'name': 'pe9', 'cn': '市盈率TTM'},
    'PBNEWMRQ': {'name': 'pbnewmrq', 'cn': '市净率MRQ'},
    'PETTMDEDUCTED': {'name': 'pettmdeducted', 'cn': '市盈率TTM扣非'},
    'PS9': {'name': 'ps9', 'cn': '市销率TTM'},
    'PCFJYXJL9': {'name': 'pcfjyxjl9', 'cn': '市现率TTM'},
    'PREDICT_PE_SYEAR': {'name': 'predict_pe_syear', 'cn': '预测市盈率今年'},
    'PREDICT_PE_NYEAR': {'name': 'predict_pe_nyear', 'cn': '预测市盈率明年'},
    'TOTAL_MARKET_CAP': {'name': 'total_market_cap', 'cn': '总市值'},
    'FREE_CAP': {'name': 'free_cap', 'cn': '流通市值'},
    'DTSYL': {'name': 'dtsyl', 'cn': '动态市盈率'},
    'YCPEG': {'name': 'ycpeg', 'cn': '预测PEG'},
    'ENTERPRISE_VALUE_MULTIPLE': {'name': 'enterprise_value_multiple', 'cn': '企业价值倍数'},
    
    # 每股指标
    'BASIC_EPS': {'name': 'basic_eps', 'cn': '每股收益'},
    'BVPS': {'name': 'bvps', 'cn': '每股净资产'},
    'PER_NETCASH_OPERATE': {'name': 'per_netcash_operate', 'cn': '每股经营现金流'},
    'PER_FCFE': {'name': 'per_fcfe', 'cn': '每股自由现金流'},
    'PER_CAPITAL_RESERVE': {'name': 'per_capital_reserve', 'cn': '每股资本公积'},
    'PER_UNASSIGN_PROFIT': {'name': 'per_unassign_profit', 'cn': '每股未分配利润'},
    'PER_SURPLUS_RESERVE': {'name': 'per_surplus_reserve', 'cn': '每股盈余公积'},
    'PER_RETAINED_EARNING': {'name': 'per_retained_earning', 'cn': '每股留存收益'},
    
    # 财务指标
    'PARENT_NETPROFIT': {'name': 'parent_netprofit', 'cn': '归属净利润'},
    'DEDUCT_NETPROFIT': {'name': 'deduct_netprofit', 'cn': '扣非净利润'},
    'TOTAL_OPERATE_INCOME': {'name': 'total_operate_income', 'cn': '营业总收入'},
    'ROE_WEIGHT': {'name': 'roe_weight', 'cn': '净资产收益率ROE'},
    'JROA': {'name': 'jroa', 'cn': '总资产净利率ROA'},
    'ROIC': {'name': 'roic', 'cn': '投入资本回报率ROIC'},
    'ZXGXL': {'name': 'zxgxl', 'cn': '最新股息率'},
    'SALE_GPR': {'name': 'sale_gpr', 'cn': '毛利率'},
    'SALE_NPR': {'name': 'sale_npr', 'cn': '净利率'},
    
    # 增长率指标
    'NETPROFIT_YOY_RATIO': {'name': 'netprofit_yoy_ratio', 'cn': '净利润增长率'},
    'DEDUCT_NETPROFIT_GROWTHRATE': {'name': 'deduct_netprofit_growthrate', 'cn': '扣非净利润增长率'},
    'TOI_YOY_RATIO': {'name': 'toi_yoy_ratio', 'cn': '营收增长率'},
    'NETPROFIT_GROWTHRATE_3Y': {'name': 'netprofit_growthrate_3y', 'cn': '净利润3年复合增长率'},
    'INCOME_GROWTHRATE_3Y': {'name': 'income_growthrate_3y', 'cn': '营收3年复合增长率'},
    'PREDICT_NETPROFIT_RATIO': {'name': 'predict_netprofit_ratio', 'cn': '预测净利润同比增长'},
    'PREDICT_INCOME_RATIO': {'name': 'predict_income_ratio', 'cn': '预测营收同比增长'},
    'BASICEPS_YOY_RATIO': {'name': 'basiceps_yoy_ratio', 'cn': '每股收益同比增长率'},
    'TOTAL_PROFIT_GROWTHRATE': {'name': 'total_profit_growthrate', 'cn': '利润总额同比增长率'},
    'OPERATE_PROFIT_GROWTHRATE': {'name': 'operate_profit_growthrate', 'cn': '营业利润同比增长率'},
    
    # 偿债能力
    'DEBT_ASSET_RATIO': {'name': 'debt_asset_ratio', 'cn': '资产负债率'},
    'EQUITY_RATIO': {'name': 'equity_ratio', 'cn': '产权比率'},
    'EQUITY_MULTIPLIER': {'name': 'equity_multiplier', 'cn': '权益乘数'},
    'CURRENT_RATIO': {'name': 'current_ratio', 'cn': '流动比率'},
    'SPEED_RATIO': {'name': 'speed_ratio', 'cn': '速动比率'},
    
    # 股本结构
    'TOTAL_SHARES': {'name': 'total_shares', 'cn': '总股本'},
    'FREE_SHARES': {'name': 'free_shares', 'cn': '流通股本'},
    
    # 股东信息
    'HOLDER_NEWEST': {'name': 'holder_newest', 'cn': '最新股东户数'},
    'HOLDER_RATIO': {'name': 'holder_ratio', 'cn': '股东户数增长率'},
    'HOLD_AMOUNT': {'name': 'hold_amount', 'cn': '户均持股金额'},
    'AVG_HOLD_NUM': {'name': 'avg_hold_num', 'cn': '户均持股数量'},
    'HOLDNUM_GROWTHRATE_3Q': {'name': 'holdnum_growthrate_3q', 'cn': '户均持股数季度增长率'},
    'HOLDNUM_GROWTHRATE_HY': {'name': 'holdnum_growthrate_hy', 'cn': '户均持股数半年增长率'},
    'HOLD_RATIO_COUNT': {'name': 'hold_ratio_count', 'cn': '十大股东持股比例合计'},
    'FREE_HOLD_RATIO': {'name': 'free_hold_ratio', 'cn': '十大流通股东比例合计'},
    
    # 技术指标信号
    'MACD_GOLDEN_FORK': {'name': 'macd_golden_fork', 'cn': 'MACD金叉日线'},
    'MACD_GOLDEN_FORKZ': {'name': 'macd_golden_forkz', 'cn': 'MACD金叉周线'},
    'MACD_GOLDEN_FORKY': {'name': 'macd_golden_forky', 'cn': 'MACD金叉月线'},
    'KDJ_GOLDEN_FORK': {'name': 'kdj_golden_fork', 'cn': 'KDJ金叉日线'},
    'KDJ_GOLDEN_FORKZ': {'name': 'kdj_golden_forkz', 'cn': 'KDJ金叉周线'},
    'KDJ_GOLDEN_FORKY': {'name': 'kdj_golden_forky', 'cn': 'KDJ金叉月线'},
    
    # 突破信号
    'BREAK_THROUGH': {'name': 'break_through', 'cn': '放量突破'},
    'LOW_FUNDS_INFLOW': {'name': 'low_funds_inflow', 'cn': '低位资金净流入'},
    'HIGH_FUNDS_OUTFLOW': {'name': 'high_funds_outflow', 'cn': '高位资金净流出'},
    'BREAKUP_MA_5DAYS': {'name': 'breakup_ma_5days', 'cn': '向上突破均线5日'},
    'BREAKUP_MA_10DAYS': {'name': 'breakup_ma_10days', 'cn': '向上突破均线10日'},
    'BREAKUP_MA_20DAYS': {'name': 'breakup_ma_20days', 'cn': '向上突破均线20日'},
    'BREAKUP_MA_30DAYS': {'name': 'breakup_ma_30days', 'cn': '向上突破均线30日'},
    'BREAKUP_MA_60DAYS': {'name': 'breakup_ma_60days', 'cn': '向上突破均线60日'},
    
    # 均线排列
    'LONG_AVG_ARRAY': {'name': 'long_avg_array', 'cn': '均线多头排列'},
    'SHORT_AVG_ARRAY': {'name': 'short_avg_array', 'cn': '均线空头排列'},
    
    # 量价关系
    'UPPER_LARGE_VOLUME': {'name': 'upper_large_volume', 'cn': '连涨放量'},
    'DOWN_NARROW_VOLUME': {'name': 'down_narrow_volume', 'cn': '下跌无量'},
    
    # K线形态
    'ONE_DAYANG_LINE': {'name': 'one_dayang_line', 'cn': '一根大阳线'},
    'TWO_DAYANG_LINES': {'name': 'two_dayang_lines', 'cn': '两根大阳线'},
    'RISE_SUN': {'name': 'rise_sun', 'cn': '旭日东升'},
    'POWER_FULGUN': {'name': 'power_fulgun', 'cn': '强势多方炮'},
    'RESTORE_JUSTICE': {'name': 'restore_justice', 'cn': '拨云见日'},
    'DOWN_7DAYS': {'name': 'down_7days', 'cn': '七连阴'},
    'UPPER_8DAYS': {'name': 'upper_8days', 'cn': '八连阳'},
    'UPPER_9DAYS': {'name': 'upper_9days', 'cn': '九连阳'},
    'UPPER_4DAYS': {'name': 'upper_4days', 'cn': '四串阳'},
    'HEAVEN_RULE': {'name': 'heaven_rule', 'cn': '天量法则'},
    'UPSIDE_VOLUME': {'name': 'upside_volume', 'cn': '放量上攻'},
    'BEARISH_ENGULFING': {'name': 'bearish_engulfing', 'cn': '穿头破脚'},
    'REVERSING_HAMMER': {'name': 'reversing_hammer', 'cn': '倒转锤头'},
    'SHOOTING_STAR': {'name': 'shooting_star', 'cn': '射击之星'},
    'EVENING_STAR': {'name': 'evening_star', 'cn': '黄昏之星'},
    'FIRST_DAWN': {'name': 'first_dawn', 'cn': '曙光初现'},
    'PREGNANT': {'name': 'pregnant', 'cn': '身怀六甲'},
    'BLACK_CLOUD_TOPS': {'name': 'black_cloud_tops', 'cn': '乌云盖顶'},
    'MORNING_STAR': {'name': 'morning_star', 'cn': '早晨之星'},
    'NARROW_FINISH': {'name': 'narrow_finish', 'cn': '窄幅整理'},
    
    # 涨跌停统计
    'LIMITED_LIFT_F6M': {'name': 'limited_lift_f6m', 'cn': '限售解禁未来半年'},
    'LIMITED_LIFT_F1Y': {'name': 'limited_lift_f1y', 'cn': '限售解禁未来1年'},
    'LIMITED_LIFT_6M': {'name': 'limited_lift_6m', 'cn': '限售解禁近半年'},
    'LIMITED_LIFT_1Y': {'name': 'limited_lift_1y', 'cn': '限售解禁近1年'},
    'DIRECTIONAL_SEO_1M': {'name': 'directional_seo_1m', 'cn': '定向增发近1个月'},
    'DIRECTIONAL_SEO_3M': {'name': 'directional_seo_3m', 'cn': '定向增发近3个月'},
    'DIRECTIONAL_SEO_6M': {'name': 'directional_seo_6m', 'cn': '定向增发近6个月'},
    'DIRECTIONAL_SEO_1Y': {'name': 'directional_seo_1y', 'cn': '定向增发近1年'},
    'RECAPITALIZE_1M': {'name': 'recapitalize_1m', 'cn': '资产重组近1个月'},
    'RECAPITALIZE_3M': {'name': 'recapitalize_3m', 'cn': '资产重组近3个月'},
    'RECAPITALIZE_6M': {'name': 'recapitalize_6m', 'cn': '资产重组近6个月'},
    'RECAPITALIZE_1Y': {'name': 'recapitalize_1y', 'cn': '资产重组近1年'},
    'EQUITY_PLEDGE_1M': {'name': 'equity_pledge_1m', 'cn': '股权质押近1个月'},
    'EQUITY_PLEDGE_3M': {'name': 'equity_pledge_3m', 'cn': '股权质押近3个月'},
    'EQUITY_PLEDGE_6M': {'name': 'equity_pledge_6m', 'cn': '股权质押近6个月'},
    'EQUITY_PLEDGE_1Y': {'name': 'equity_pledge_1y', 'cn': '股权质押近1年'},
    'PLEDGE_RATIO': {'name': 'pledge_ratio', 'cn': '质押比例'},
    'GOODWILL_SCALE': {'name': 'goodwill_scale', 'cn': '商誉规模'},
    'GOODWILL_ASSETS_RATRO': {'name': 'goodwill_assets_ratro', 'cn': '商誉占净资产比例'},
    'PREDICT_TYPE': {'name': 'predict_type', 'cn': '业绩预告'},
    'PAR_DIVIDEND_PRETAX': {'name': 'par_dividend_pretax', 'cn': '每股股利税前'},
    'PAR_DIVIDEND': {'name': 'par_dividend', 'cn': '每股红股'},
    'PAR_IT_EQUITY': {'name': 'par_it_equity', 'cn': '每股转增股本'},
    'HOLDER_CHANGE_3M': {'name': 'holder_change_3m', 'cn': '近3月股东增减比例'},
    'EXECUTIVE_CHANGE_3M': {'name': 'executive_change_3m', 'cn': '近3月高管增减比例'},
    'ORG_SURVEY_3M': {'name': 'org_survey_3m', 'cn': '近3月机构调研'},
    'ORG_RATING': {'name': 'org_rating', 'cn': '机构评级'},
    'ALLCORP_NUM': {'name': 'allcorp_num', 'cn': '机构持股家数合计'},
    'ALLCORP_FUND_NUM': {'name': 'allcorp_fund_num', 'cn': '基金持股家数'},
    'ALLCORP_QS_NUM': {'name': 'allcorp_qs_num', 'cn': '券商持股家数'},
    'ALLCORP_QFII_NUM': {'name': 'allcorp_qfii_num', 'cn': 'QFII持股家数'},
    'ALLCORP_BX_NUM': {'name': 'allcorp_bx_num', 'cn': '保险公司持股家数'},
    'ALLCORP_SB_NUM': {'name': 'allcorp_sb_num', 'cn': '社保持股家数'},
    'ALLCORP_XT_NUM': {'name': 'allcorp_xt_num', 'cn': '信托公司持股家数'},
    'ALLCORP_RATIO': {'name': 'allcorp_ratio', 'cn': '机构持股比例合计'},
    'ALLCORP_FUND_RATIO': {'name': 'allcorp_fund_ratio', 'cn': '基金持股比例'},
    'ALLCORP_QS_RATIO': {'name': 'allcorp_qs_ratio', 'cn': '券商持股比例'},
    'ALLCORP_QFII_RATIO': {'name': 'allcorp_qfii_ratio', 'cn': 'QFII持股比例'},
    'ALLCORP_BX_RATIO': {'name': 'allcorp_bx_ratio', 'cn': '保险公司持股比例'},
    'ALLCORP_SB_RATIO': {'name': 'allcorp_sb_ratio', 'cn': '社保持股比例'},
    'ALLCORP_XT_RATIO': {'name': 'allcorp_xt_ratio', 'cn': '信托公司持股比例'},
    'POPULARITY_RANK': {'name': 'popularity_rank', 'cn': '股吧人气排名'},
    'RANK_CHANGE': {'name': 'rank_change', 'cn': '人气排名变化'},
    'UPP_DAYS': {'name': 'upp_days', 'cn': '人气排名连涨'},
    'DOWN_DAYS': {'name': 'down_days', 'cn': '人气排名连跌'},
    'NEW_HIGH': {'name': 'new_high', 'cn': '人气排名创新高'},
    'NEW_DOWN': {'name': 'new_down', 'cn': '人气排名创新低'},
    'NEWFANS_RATIO': {'name': 'newfans_ratio', 'cn': '新晋粉丝占比'},
    'BIGFANS_RATIO': {'name': 'bigfans_ratio', 'cn': '铁杆粉丝占比'},
    'CONCERN_RANK_7DAYS': {'name': 'concern_rank_7days', 'cn': '7日关注排名'},
    'BROWSE_RANK': {'name': 'browse_rank', 'cn': '今日浏览排名'},
    'IS_ISSUE_BREAK': {'name': 'is_issue_break', 'cn': '破发股票'},
    'IS_BPS_BREAK': {'name': 'is_bps_break', 'cn': '破净股票'},
    'NOW_NEWHIGH': {'name': 'now_newhigh', 'cn': '今日创历史新高'},
    'NOW_NEWLOW': {'name': 'now_newlow', 'cn': '今日创历史新低'},
    'HIGH_RECENT_3DAYS': {'name': 'high_recent_3days', 'cn': '近期创历史新高近3日'},
    'HIGH_RECENT_5DAYS': {'name': 'high_recent_5days', 'cn': '近期创历史新高近5日'},
    'HIGH_RECENT_10DAYS': {'name': 'high_recent_10days', 'cn': '近期创历史新高近10日'},
    'HIGH_RECENT_20DAYS': {'name': 'high_recent_20days', 'cn': '近期创历史新高近20日'},
    'HIGH_RECENT_30DAYS': {'name': 'high_recent_30days', 'cn': '近期创历史新高近30日'},
    'LOW_RECENT_3DAYS': {'name': 'low_recent_3days', 'cn': '近期创历史新低近3日'},
    'LOW_RECENT_5DAYS': {'name': 'low_recent_5days', 'cn': '近期创历史新低近5日'},
    'LOW_RECENT_10DAYS': {'name': 'low_recent_10days', 'cn': '近期创历史新低近10日'},
    'LOW_RECENT_20DAYS': {'name': 'low_recent_20days', 'cn': '近期创历史新低近20日'},
    'LOW_RECENT_30DAYS': {'name': 'low_recent_30days', 'cn': '近期创历史新低近30日'},
    'WIN_MARKET_3DAYS': {'name': 'win_market_3days', 'cn': '近期跑赢大盘近3日'},
    'WIN_MARKET_5DAYS': {'name': 'win_market_5days', 'cn': '近期跑赢大盘近5日'},
    'WIN_MARKET_10DAYS': {'name': 'win_market_10days', 'cn': '近期跑赢大盘近10日'},
    'WIN_MARKET_20DAYS': {'name': 'win_market_20days', 'cn': '近期跑赢大盘近20日'},
    'WIN_MARKET_30DAYS': {'name': 'win_market_30days', 'cn': '近期跑赢大盘近30日'},
    'NET_INFLOW': {'name': 'net_inflow', 'cn': '当日净流入额'},
    'NETINFLOW_3DAYS': {'name': 'netinflow_3days', 'cn': '3日主力净流入'},
    'NETINFLOW_5DAYS': {'name': 'netinflow_5days', 'cn': '5日主力净流入'},
    'NOWINTERST_RATIO': {'name': 'nowinterst_ratio', 'cn': '当日增仓占比'},
    'NOWINTERST_RATIO_3D': {'name': 'nowinterst_ratio_3d', 'cn': '3日增仓占比'},
    'NOWINTERST_RATIO_5D': {'name': 'nowinterst_ratio_5d', 'cn': '5日增仓占比'},
    'DDX': {'name': 'ddx', 'cn': '当日DDX'},
    'DDX_3D': {'name': 'ddx_3d', 'cn': '3日DDX'},
    'DDX_5D': {'name': 'ddx_5d', 'cn': '5日DDX'},
    'DDX_RED_10D': {'name': 'ddx_red_10d', 'cn': '10日内DDX飘红天数'},
    'CHANGERATE_3DAYS': {'name': 'changerate_3days', 'cn': '3日涨跌幅'},
    'CHANGERATE_5DAYS': {'name': 'changerate_5days', 'cn': '5日涨跌幅'},
    'CHANGERATE_10DAYS': {'name': 'changerate_10days', 'cn': '10日涨跌幅'},
    'CHANGERATE_TY': {'name': 'changerate_ty', 'cn': '今年以来涨跌幅'},
    'UPNDAY': {'name': 'upnday', 'cn': '连涨天数'},
    'DOWNNDAY': {'name': 'downnday', 'cn': '连跌天数'},
    'LISTING_YIELD_YEAR': {'name': 'listing_yield_year', 'cn': '上市以来年化收益率'},
    'LISTING_VOLATILITY_YEAR': {'name': 'listing_volatility_year', 'cn': '上市以来年化波动率'},
    'MUTUAL_NETBUY_AMT': {'name': 'mutual_netbuy_amt', 'cn': '沪深股通净买入金额'},
    'HOLD_RATIO': {'name': 'hold_ratio', 'cn': '沪深股通持股比例'},
    'MA5': {'name': 'ma5', 'cn': '5日均线'},
    'MA10': {'name': 'ma10', 'cn': '10日均线'},
    'MA20': {'name': 'ma20', 'cn': '20日均线'},
    'MA60': {'name': 'ma60', 'cn': '60日均线'},
    'MA120': {'name': 'ma120', 'cn': '120日均线'},
    'MA250': {'name': 'ma250', 'cn': '250日均线'},
}


class EastmoneySelectionFetcher(BaseFetcher):
    """东方财富网选股器数据获取器"""

    def __init__(self):
        super().__init__()
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://data.eastmoney.com/xuangu/'
        })

    def _fetch_raw_data(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从数据源获取原始数据（选股器不支持单股查询）"""
        return pd.DataFrame()

    def _normalize_data(self, df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        """标准化数据列名"""
        return df

    def fetch_selection_data(
        self,
        page_size: int = 50,
        filter_str: str = "(MARKET+in+(\"上交所主板\",\"深交所主板\",\"深交所创业板\"))(NEW_PRICE>0)"
    ) -> Optional[pd.DataFrame]:
        """
        从东方财富网获取选股器数据
        
        Args:
            page_size: 每页大小
            filter_str: 过滤条件
            
        Returns:
            选股数据 DataFrame
        """
        url = "https://data.eastmoney.com/dataapi/xuangu/list"
        
        # 构建字段列表
        sty = ",".join(SELECTION_COLUMNS.keys())
        
        params = {
            "sty": sty,
            "filter": filter_str,
            "p": 1,
            "ps": page_size,
            "source": "SELECT_SECURITIES",
            "client": "WEB"
        }
        
        try:
            logger.info("[eastmoney] 开始获取选股器数据")
            r = self._session.get(url, params=params, timeout=30)
            r.raise_for_status()
            data_json = r.json()
            
            result = data_json.get("result", {})
            data = result.get("data", [])
            
            if not data:
                logger.info("[eastmoney] 未获取到选股数据")
                return pd.DataFrame()

            data_count = result.get("count", 0)
            page_count = math.ceil(data_count / page_size)
            
            logger.info(f"[eastmoney] 共 {data_count} 条数据，{page_count} 页")
            
            # 如果有多页，继续获取
            while page_count > 1:
                time.sleep(random.uniform(1, 1.5))
                params["p"] = params["p"] + 1
                r = self._session.get(url, params=params, timeout=30)
                r.raise_for_status()
                data_json = r.json()
                _data = data_json.get("result", {}).get("data", [])
                data.extend(_data)
                page_count -= 1
            
            temp_df = pd.DataFrame(data)
            
            # 处理概念和风格字段（数组转字符串）
            if 'CONCEPT' in temp_df.columns:
                mask = ~temp_df['CONCEPT'].isna()
                temp_df.loc[mask, 'CONCEPT'] = temp_df.loc[mask, 'CONCEPT'].apply(
                    lambda x: ', '.join(x) if isinstance(x, list) else str(x)
                )
            if 'STYLE' in temp_df.columns:
                mask = ~temp_df['STYLE'].isna()
                temp_df.loc[mask, 'STYLE'] = temp_df.loc[mask, 'STYLE'].apply(
                    lambda x: ', '.join(x) if isinstance(x, list) else str(x)
                )
            
            # 处理 flag 类型字段（将 None 转换为 '0'）
            flag_fields = [
                'IS_ISSUE_BREAK', 'IS_BPS_BREAK', 'NOW_NEWHIGH', 'NOW_NEWLOW',
                'HIGH_RECENT_3DAYS', 'HIGH_RECENT_5DAYS', 'HIGH_RECENT_10DAYS',
                'HIGH_RECENT_20DAYS', 'HIGH_RECENT_30DAYS', 'LOW_RECENT_3DAYS',
                'LOW_RECENT_5DAYS', 'LOW_RECENT_10DAYS', 'LOW_RECENT_20DAYS',
                'LOW_RECENT_30DAYS', 'WIN_MARKET_3DAYS', 'WIN_MARKET_5DAYS',
                'WIN_MARKET_10DAYS', 'WIN_MARKET_20DAYS', 'WIN_MARKET_30DAYS',
                'DIRECTIONAL_SEO_1M', 'DIRECTIONAL_SEO_3M', 'DIRECTIONAL_SEO_6M',
                'DIRECTIONAL_SEO_1Y', 'RECAPITALIZE_1M', 'RECAPITALIZE_3M',
                'RECAPITALIZE_6M', 'RECAPITALIZE_1Y', 'EQUITY_PLEDGE_1M',
                'EQUITY_PLEDGE_3M', 'EQUITY_PLEDGE_6M', 'EQUITY_PLEDGE_1Y',
            ]
            for field in flag_fields:
                if field in temp_df.columns:
                    temp_df[field] = temp_df[field].fillna('0').astype(str)
            
            # 用 PE9 作为 PE 的值，因为东方财富 API 不直接返回 PE 字段
            if 'PE9' in temp_df.columns:
                temp_df['PE'] = temp_df['PE9'].copy()
            
            # 类型转换
            for api_key, info in SELECTION_COLUMNS.items():
                if api_key in temp_df.columns:
                    # 浮点类型字段
                    if info['name'] in [
                        'new_price', 'change_rate', 'volume_ratio', 'high_price', 'low_price', 
                        'pre_close_price', 'turnoverrate', 'amplitude', 'pe', 'pe9', 'pb', 'pbnewmrq', 
                        'pettmdeducted', 'ps9', 'pcfjyxjl9', 'predict_pe_syear', 'predict_pe_nyear',
                        'dtsyl', 'ycpeg', 'enterprise_value_multiple', 'basic_eps', 'bvps',
                        'per_netcash_operate', 'per_fcfe', 'per_capital_reserve', 'per_unassign_profit',
                        'per_surplus_reserve', 'per_retained_earning', 'roe_weight', 'jroa',
                        'roic', 'sale_gpr', 'sale_npr', 'zxgxl', 'netprofit_yoy_ratio',
                        'deduct_netprofit_growthrate', 'toi_yoy_ratio', 'netprofit_growthrate_3y',
                        'income_growthrate_3y', 'predict_netprofit_ratio', 'predict_income_ratio',
                        'basiceps_yoy_ratio', 'total_profit_growthrate', 'operate_profit_growthrate',
                        'debt_asset_ratio', 'equity_ratio', 'equity_multiplier', 'current_ratio',
                        'speed_ratio', 'holder_ratio', 'avg_hold_num', 'holdnum_growthrate_3q',
                        'holdnum_growthrate_hy', 'hold_ratio_count', 'free_hold_ratio',
                        'pledge_ratio', 'goodwill_assets_ratro', 'par_dividend_pretax',
                        'par_dividend', 'par_it_equity', 'holder_change_3m',
                        'executive_change_3m', 'allcorp_ratio', 'allcorp_fund_ratio',
                        'allcorp_qs_ratio', 'allcorp_qfii_ratio', 'allcorp_bx_ratio',
                        'allcorp_sb_ratio', 'allcorp_xt_ratio', 'newfans_ratio', 'bigfans_ratio',
                        'net_inflow', 'nowinterst_ratio', 'nowinterst_ratio_3d',
                        'nowinterst_ratio_5d', 'ddx', 'ddx_3d', 'ddx_5d',
                        'changerate_3days', 'changerate_5days', 'changerate_10days',
                        'changerate_ty', 'listing_yield_year', 'listing_volatility_year',
                        'hold_ratio', 'ma5', 'ma10', 'ma20', 'ma60', 'ma120', 'ma250'
                    ]:
                        temp_df[api_key] = pd.to_numeric(temp_df[api_key], errors="coerce")
                    # 整数/大数值字段
                    elif info['name'] in [
                        'volume', 'deal_amount', 'total_market_cap', 'free_cap', 'parent_netprofit',
                        'deduct_netprofit', 'total_operate_income', 'total_shares', 'free_shares',
                        'holder_newest', 'hold_amount', 'main_funds_net', 'netinflow_3days',
                        'netinflow_5days', 'ddx_red_10d', 'upnday', 'downnday',
                        'mutual_netbuy_amt', 'org_survey_3m', 'allcorp_num',
                        'allcorp_fund_num', 'allcorp_qs_num', 'allcorp_qfii_num',
                        'allcorp_bx_num', 'allcorp_sb_num', 'allcorp_xt_num',
                        'popularity_rank', 'rank_change', 'upp_days', 'down_days',
                        'new_high', 'new_down', 'concern_rank_7days', 'browse_rank'
                    ]:
                        temp_df[api_key] = pd.to_numeric(temp_df[api_key], errors="coerce")
                    # 日期字段
                    elif info['name'] in ['listing_date', 'date']:
                        temp_df[api_key] = pd.to_datetime(temp_df[api_key], errors="coerce").dt.date
            
            # 重命名字段
            rename_map = {k: v['name'] for k, v in SELECTION_COLUMNS.items() if k in temp_df.columns}
            temp_df = temp_df.rename(columns=rename_map)
            
            logger.info(f"[eastmoney] 获取选股数据成功，共 {len(temp_df)} 条")
            return temp_df
            
        except requests.RequestException as e:
            logger.error(f"[eastmoney] 请求选股数据失败: {e}")
            return None
        except Exception as e:
            logger.error(f"[eastmoney] 处理选股数据异常: {e}")
            logger.exception(e)
            return None
