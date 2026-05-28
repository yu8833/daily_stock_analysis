import React, { useEffect, useState, useRef } from 'react';
import { Card, Badge, EmptyState, Loading } from '../components/common';
import { Search, ExternalLink, Filter, ChevronDown, ArrowUp, ArrowDown, X, Check, Download } from 'lucide-react';

interface SelectionStock {
  code: string;
  name: string;
  new_price: number | null;
  change_rate: number | null;
  volume_ratio: number | null;
  high_price: number | null;
  low_price: number | null;
  pre_close_price: number | null;
  volume: number | null;
  deal_amount: number | null;
  turnoverrate: number | null;
  amplitude: number | null;
  listing_date: string | null;
  industry: string | null;
  area: string | null;
  concept: string | null;
  style: string | null;
  is_hs300: string | null;
  is_sz50: string | null;
  is_zz500: string | null;
  is_zz1000: string | null;
  is_cy50: string | null;
  pe: number | null;
  pe9: number | null;
  pbnewmrq: number | null;
  pettmdeducted: number | null;
  ps9: number | null;
  pcfjyxjl9: number | null;
  predict_pe_syear: number | null;
  predict_pe_nyear: number | null;
  dtsyl: number | null;
  ycpeg: number | null;
  enterprise_value_multiple: number | null;
  total_market_cap: number | null;
  free_cap: number | null;
  basic_eps: number | null;
  bvps: number | null;
  per_netcash_operate: number | null;
  per_fcfe: number | null;
  per_capital_reserve: number | null;
  per_unassign_profit: number | null;
  per_surplus_reserve: number | null;
  per_retained_earning: number | null;
  parent_netprofit: number | null;
  deduct_netprofit: number | null;
  total_operate_income: number | null;
  roe_weight: number | null;
  jroa: number | null;
  roic: number | null;
  zxgxl: number | null;
  sale_gpr: number | null;
  sale_npr: number | null;
  netprofit_yoy_ratio: number | null;
  deduct_netprofit_growthrate: number | null;
  toi_yoy_ratio: number | null;
  netprofit_growthrate_3y: number | null;
  income_growthrate_3y: number | null;
  predict_netprofit_ratio: number | null;
  predict_income_ratio: number | null;
  basiceps_yoy_ratio: number | null;
  total_profit_growthrate: number | null;
  operate_profit_growthrate: number | null;
  debt_asset_ratio: number | null;
  equity_ratio: number | null;
  equity_multiplier: number | null;
  current_ratio: number | null;
  speed_ratio: number | null;
  total_shares: number | null;
  free_shares: number | null;
  holder_newest: number | null;
  holder_ratio: number | null;
  hold_amount: number | null;
  avg_hold_num: number | null;
  holdnum_growthrate_3q: number | null;
  holdnum_growthrate_hy: number | null;
  hold_ratio_count: number | null;
  free_hold_ratio: number | null;
  macd_golden_fork: string | null;
  macd_golden_forkz: string | null;
  macd_golden_forky: string | null;
  kdj_golden_fork: string | null;
  kdj_golden_forkz: string | null;
  kdj_golden_forky: string | null;
  break_through: string | null;
  low_funds_inflow: string | null;
  high_funds_outflow: string | null;
  breakup_ma_5days: string | null;
  breakup_ma_10days: string | null;
  breakup_ma_20days: string | null;
  breakup_ma_30days: string | null;
  breakup_ma_60days: string | null;
  long_avg_array: string | null;
  short_avg_array: string | null;
  upper_large_volume: string | null;
  down_narrow_volume: string | null;
  one_dayang_line: string | null;
  two_dayang_lines: string | null;
  rise_sun: string | null;
  power_fulgun: string | null;
  restore_justice: string | null;
  down_7days: string | null;
  upper_8days: string | null;
  upper_9days: string | null;
  upper_4days: string | null;
  heaven_rule: string | null;
  upside_volume: string | null;
  bearish_engulfing: string | null;
  reversing_hammer: string | null;
  shooting_star: string | null;
  evening_star: string | null;
  first_dawn: string | null;
  pregnant: string | null;
  black_cloud_tops: string | null;
  morning_star: string | null;
  narrow_finish: string | null;
  limited_lift_f6m: string | null;
  limited_lift_f1y: string | null;
  limited_lift_6m: string | null;
  limited_lift_1y: string | null;
  directional_seo_1m: string | null;
  directional_seo_3m: string | null;
  directional_seo_6m: string | null;
  directional_seo_1y: string | null;
  recapitalize_1m: string | null;
  recapitalize_3m: string | null;
  recapitalize_6m: string | null;
  recapitalize_1y: string | null;
  equity_pledge_1m: string | null;
  equity_pledge_3m: string | null;
  equity_pledge_6m: string | null;
  equity_pledge_1y: string | null;
  pledge_ratio: number | null;
  goodwill_scale: number | null;
  goodwill_assets_ratro: number | null;
  predict_type: string | null;
  par_dividend_pretax: number | null;
  par_dividend: number | null;
  par_it_equity: number | null;
  holder_change_3m: number | null;
  executive_change_3m: number | null;
  org_survey_3m: number | null;
  org_rating: string | null;
  allcorp_num: number | null;
  allcorp_fund_num: number | null;
  allcorp_qs_num: number | null;
  allcorp_qfii_num: number | null;
  allcorp_bx_num: number | null;
  allcorp_sb_num: number | null;
  allcorp_xt_num: number | null;
  allcorp_ratio: number | null;
  allcorp_fund_ratio: number | null;
  allcorp_qs_ratio: number | null;
  allcorp_qfii_ratio: number | null;
  allcorp_bx_ratio: number | null;
  allcorp_sb_ratio: number | null;
  allcorp_xt_ratio: number | null;
  popularity_rank: number | null;
  rank_change: number | null;
  upp_days: number | null;
  down_days: number | null;
  new_high: number | null;
  new_down: number | null;
  newfans_ratio: number | null;
  bigfans_ratio: number | null;
  concern_rank_7days: number | null;
  browse_rank: number | null;
  is_issue_break: string | null;
  is_bps_break: string | null;
  now_newhigh: string | null;
  now_newlow: string | null;
  high_recent_3days: string | null;
  high_recent_5days: string | null;
  high_recent_10days: string | null;
  high_recent_20days: string | null;
  high_recent_30days: string | null;
  low_recent_3days: string | null;
  low_recent_5days: string | null;
  low_recent_10days: string | null;
  low_recent_20days: string | null;
  low_recent_30days: string | null;
  win_market_3days: string | null;
  win_market_5days: string | null;
  win_market_10days: string | null;
  win_market_20days: string | null;
  win_market_30days: string | null;
  net_inflow: number | null;
  netinflow_3days: number | null;
  netinflow_5days: number | null;
  nowinterst_ratio: number | null;
  nowinterst_ratio_3d: number | null;
  nowinterst_ratio_5d: number | null;
  ddx: number | null;
  ddx_3d: number | null;
  ddx_5d: number | null;
  ddx_red_10d: number | null;
  changerate_3days: number | null;
  changerate_5days: number | null;
  changerate_10days: number | null;
  changerate_ty: number | null;
  upnday: number | null;
  downnday: number | null;
  listing_yield_year: number | null;
  listing_volatility_year: number | null;
  mutual_netbuy_amt: number | null;
  hold_ratio: number | null;
}

type SortField = keyof SelectionStock;
type SortOrder = 'asc' | 'desc';

const COLUMN_CONFIG: { key: SortField; label: string; width: string; align: 'left' | 'right' | 'center'; type: 'text' | 'number' | 'percent' | 'money' | 'price' | 'date' | 'flag' }[] = [
  { key: 'code', label: '代码', width: 'w-16', align: 'left', type: 'text' },
  { key: 'name', label: '名称', width: 'w-20', align: 'left', type: 'text' },
  { key: 'is_issue_break', label: '破发', width: 'w-14', align: 'center', type: 'flag' },
  { key: 'is_bps_break', label: '破净', width: 'w-14', align: 'center', type: 'flag' },
  { key: 'is_hs300', label: '沪深300', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'is_sz50', label: '上证50', width: 'w-14', align: 'center', type: 'flag' },
  { key: 'is_zz500', label: '中证500', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'is_zz1000', label: '中证1000', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'is_cy50', label: '创业板50', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'macd_golden_fork', label: 'MACD金叉', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'macd_golden_forkz', label: 'MACD周金叉', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'macd_golden_forky', label: 'MACD月金叉', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'kdj_golden_fork', label: 'KDJ金叉', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'kdj_golden_forkz', label: 'KDJ周金叉', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'kdj_golden_forky', label: 'KDJ月金叉', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'break_through', label: '放量突破', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'low_funds_inflow', label: '低位资金净流入', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'high_funds_outflow', label: '高位资金净流出', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'breakup_ma_5days', label: '站5日线', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'breakup_ma_10days', label: '站10日线', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'breakup_ma_20days', label: '站20日线', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'breakup_ma_30days', label: '站30日线', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'breakup_ma_60days', label: '站60日线', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'long_avg_array', label: '均线多头', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'short_avg_array', label: '均线空头', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'upper_large_volume', label: '连涨放量', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'down_narrow_volume', label: '下跌无量', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'one_dayang_line', label: '大阳线', width: 'w-14', align: 'center', type: 'flag' },
  { key: 'two_dayang_lines', label: '两连阳', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'rise_sun', label: '旭日东升', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'power_fulgun', label: '强势多方炮', width: 'w-20', align: 'center', type: 'flag' },
  { key: 'restore_justice', label: '拨云见日', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'down_7days', label: '七连阴', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'upper_8days', label: '八连阳', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'upper_9days', label: '九连阳', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'upper_4days', label: '四串阳', width: 'w-16', align: 'center', type: 'flag' },
  { key: 'heaven_rule', label: '天量法则', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'upside_volume', label: '放量上攻', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'bearish_engulfing', label: '穿头破脚', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'reversing_hammer', label: '倒转锤头', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'shooting_star', label: '射击之星', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'evening_star', label: '黄昏之星', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'first_dawn', label: '曙光初现', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'pregnant', label: '身怀六甲', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'black_cloud_tops', label: '乌云盖顶', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'morning_star', label: '早晨之星', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'narrow_finish', label: '窄幅整理', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'limited_lift_f6m', label: '限售解禁未来半年', width: 'w-28', align: 'center', type: 'flag' },
  { key: 'limited_lift_f1y', label: '限售解禁未来一年', width: 'w-28', align: 'center', type: 'flag' },
  { key: 'limited_lift_6m', label: '限售解禁近半年', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'limited_lift_1y', label: '限售解禁近一年', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'directional_seo_1m', label: '定增近1月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'directional_seo_3m', label: '定增近3月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'directional_seo_6m', label: '定增近6月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'directional_seo_1y', label: '定增近1年', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'recapitalize_1m', label: '重组近1月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'recapitalize_3m', label: '重组近3月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'recapitalize_6m', label: '重组近6月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'recapitalize_1y', label: '重组近1年', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'equity_pledge_1m', label: '质押近1月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'equity_pledge_3m', label: '质押近3月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'equity_pledge_6m', label: '质押近6月', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'equity_pledge_1y', label: '质押近1年', width: 'w-18', align: 'center', type: 'flag' },
  { key: 'now_newhigh', label: '今日创历史新高', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'now_newlow', label: '今日创历史新低', width: 'w-24', align: 'center', type: 'flag' },
  { key: 'high_recent_3days', label: '近期创历史新高近3日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'high_recent_5days', label: '近期创历史新高近5日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'high_recent_10days', label: '近期创历史新高近10日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'high_recent_20days', label: '近期创历史新高近20日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'high_recent_30days', label: '近期创历史新高近30日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'low_recent_3days', label: '近期创历史新低近3日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'low_recent_5days', label: '近期创历史新低近5日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'low_recent_10days', label: '近期创历史新低近10日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'low_recent_20days', label: '近期创历史新低近20日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'low_recent_30days', label: '近期创历史新低近30日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'win_market_3days', label: '近期跑赢大盘近3日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'win_market_5days', label: '近期跑赢大盘近5日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'win_market_10days', label: '近期跑赢大盘近10日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'win_market_20days', label: '近期跑赢大盘近20日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'win_market_30days', label: '近期跑赢大盘近30日', width: 'w-32', align: 'center', type: 'flag' },
  { key: 'industry', label: '行业', width: 'w-24', align: 'left', type: 'text' },
  { key: 'area', label: '地区', width: 'w-16', align: 'left', type: 'text' },
  { key: 'concept', label: '概念', width: 'w-32', align: 'left', type: 'text' },
  { key: 'new_price', label: '最新价', width: 'w-20', align: 'right', type: 'price' },
  { key: 'change_rate', label: '涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'volume_ratio', label: '量比', width: 'w-16', align: 'right', type: 'number' },
  { key: 'high_price', label: '最高价', width: 'w-20', align: 'right', type: 'price' },
  { key: 'low_price', label: '最低价', width: 'w-20', align: 'right', type: 'price' },
  { key: 'pre_close_price', label: '昨收', width: 'w-16', align: 'right', type: 'price' },
  { key: 'volume', label: '成交量', width: 'w-24', align: 'right', type: 'number' },
  { key: 'deal_amount', label: '成交额', width: 'w-24', align: 'right', type: 'money' },
  { key: 'turnoverrate', label: '换手率', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'amplitude', label: '振幅', width: 'w-16', align: 'right', type: 'percent' },
  { key: 'pe', label: 'PE', width: 'w-14', align: 'right', type: 'number' },
  { key: 'pe9', label: 'PE(TTM)', width: 'w-16', align: 'right', type: 'number' },
  { key: 'pbnewmrq', label: 'PB(MRQ)', width: 'w-18', align: 'right', type: 'number' },
  { key: 'pettmdeducted', label: 'PE扣非', width: 'w-18', align: 'right', type: 'number' },
  { key: 'ps9', label: 'PS(TTM)', width: 'w-18', align: 'right', type: 'number' },
  { key: 'pcfjyxjl9', label: 'PCF(TTM)', width: 'w-20', align: 'right', type: 'number' },
  { key: 'predict_pe_syear', label: '预测PE今年', width: 'w-24', align: 'right', type: 'number' },
  { key: 'predict_pe_nyear', label: '预测PE明年', width: 'w-24', align: 'right', type: 'number' },
  { key: 'dtsyl', label: '动态PE', width: 'w-16', align: 'right', type: 'number' },
  { key: 'ycpeg', label: 'PEG', width: 'w-14', align: 'right', type: 'number' },
  { key: 'enterprise_value_multiple', label: '企业价值倍数', width: 'w-24', align: 'right', type: 'number' },
  { key: 'total_market_cap', label: '总市值', width: 'w-24', align: 'right', type: 'money' },
  { key: 'free_cap', label: '流通市值', width: 'w-24', align: 'right', type: 'money' },
  { key: 'basic_eps', label: 'EPS', width: 'w-14', align: 'right', type: 'number' },
  { key: 'bvps', label: 'BVPS', width: 'w-14', align: 'right', type: 'number' },
  { key: 'per_netcash_operate', label: '每股经营现金流', width: 'w-24', align: 'right', type: 'number' },
  { key: 'per_fcfe', label: '每股自由现金流', width: 'w-24', align: 'right', type: 'number' },
  { key: 'per_capital_reserve', label: '每股资本公积', width: 'w-24', align: 'right', type: 'number' },
  { key: 'per_unassign_profit', label: '每股未分配利润', width: 'w-28', align: 'right', type: 'number' },
  { key: 'per_surplus_reserve', label: '每股盈余公积', width: 'w-24', align: 'right', type: 'number' },
  { key: 'per_retained_earning', label: '每股留存收益', width: 'w-24', align: 'right', type: 'number' },
  { key: 'parent_netprofit', label: '归属净利润', width: 'w-24', align: 'right', type: 'money' },
  { key: 'deduct_netprofit', label: '扣非净利润', width: 'w-24', align: 'right', type: 'money' },
  { key: 'total_operate_income', label: '营业总收入', width: 'w-24', align: 'right', type: 'money' },
  { key: 'roe_weight', label: 'ROE(加权)', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'jroa', label: 'ROA', width: 'w-14', align: 'right', type: 'percent' },
  { key: 'roic', label: 'ROIC', width: 'w-16', align: 'right', type: 'percent' },
  { key: 'zxgxl', label: '最新股息率', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'sale_gpr', label: '毛利率', width: 'w-18', align: 'right', type: 'percent' },
  { key: 'sale_npr', label: '净利率', width: 'w-18', align: 'right', type: 'percent' },
  { key: 'netprofit_yoy_ratio', label: '净利润增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'deduct_netprofit_growthrate', label: '扣非净利润增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'toi_yoy_ratio', label: '营收增长', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'netprofit_growthrate_3y', label: '净利3年复合', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'income_growthrate_3y', label: '营收3年复合', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'predict_netprofit_ratio', label: '预测净利润增长', width: 'w-28', align: 'right', type: 'percent' },
  { key: 'predict_income_ratio', label: '预测营收增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'basiceps_yoy_ratio', label: 'EPS增长', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'total_profit_growthrate', label: '利润总额增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'operate_profit_growthrate', label: '营业利润增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'debt_asset_ratio', label: '资产负债率', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'equity_ratio', label: '产权比率', width: 'w-18', align: 'right', type: 'percent' },
  { key: 'equity_multiplier', label: '权益乘数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'current_ratio', label: '流动比率', width: 'w-20', align: 'right', type: 'number' },
  { key: 'speed_ratio', label: '速动比率', width: 'w-20', align: 'right', type: 'number' },
  { key: 'total_shares', label: '总股本', width: 'w-20', align: 'right', type: 'number' },
  { key: 'free_shares', label: '流通股本', width: 'w-20', align: 'right', type: 'number' },
  { key: 'holder_newest', label: '股东户数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'holder_ratio', label: '股东户数增长', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'hold_amount', label: '户均持股金额', width: 'w-24', align: 'right', type: 'money' },
  { key: 'avg_hold_num', label: '户均持股数量', width: 'w-24', align: 'right', type: 'number' },
  { key: 'holdnum_growthrate_3q', label: '户均持股数季度增长', width: 'w-28', align: 'right', type: 'percent' },
  { key: 'holdnum_growthrate_hy', label: '户均持股数半年增长', width: 'w-28', align: 'right', type: 'percent' },
  { key: 'hold_ratio_count', label: '十大股东持股', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'free_hold_ratio', label: '十大流通股东', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'pledge_ratio', label: '质押比例', width: 'w-18', align: 'right', type: 'percent' },
  { key: 'goodwill_scale', label: '商誉规模', width: 'w-20', align: 'right', type: 'money' },
  { key: 'goodwill_assets_ratro', label: '商誉占比', width: 'w-18', align: 'right', type: 'percent' },
  { key: 'predict_type', label: '业绩预告', width: 'w-18', align: 'left', type: 'text' },
  { key: 'par_dividend_pretax', label: '每股股利税前', width: 'w-24', align: 'right', type: 'number' },
  { key: 'par_dividend', label: '每股红股', width: 'w-18', align: 'right', type: 'number' },
  { key: 'par_it_equity', label: '每股转增股本', width: 'w-24', align: 'right', type: 'number' },
  { key: 'holder_change_3m', label: '近3月股东增减', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'executive_change_3m', label: '近3月高管增减', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'org_survey_3m', label: '近3月机构调研', width: 'w-24', align: 'right', type: 'number' },
  { key: 'org_rating', label: '机构评级', width: 'w-18', align: 'left', type: 'text' },
  { key: 'allcorp_num', label: '机构家数合计', width: 'w-24', align: 'right', type: 'number' },
  { key: 'allcorp_fund_num', label: '基金家数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'allcorp_qs_num', label: '券商家数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'allcorp_qfii_num', label: 'QFII家数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'allcorp_bx_num', label: '保险家数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'allcorp_sb_num', label: '社保持股家数', width: 'w-24', align: 'right', type: 'number' },
  { key: 'allcorp_xt_num', label: '信托家数', width: 'w-20', align: 'right', type: 'number' },
  { key: 'allcorp_ratio', label: '机构比例合计', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'allcorp_fund_ratio', label: '基金比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'allcorp_qs_ratio', label: '券商比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'allcorp_qfii_ratio', label: 'QFII比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'allcorp_bx_ratio', label: '保险比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'allcorp_sb_ratio', label: '社保比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'allcorp_xt_ratio', label: '信托比例', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'popularity_rank', label: '人气排名', width: 'w-18', align: 'right', type: 'number' },
  { key: 'rank_change', label: '排名变化', width: 'w-18', align: 'right', type: 'number' },
  { key: 'upp_days', label: '人气排名连涨', width: 'w-24', align: 'right', type: 'number' },
  { key: 'down_days', label: '人气排名连跌', width: 'w-24', align: 'right', type: 'number' },
  { key: 'new_high', label: '人气排名创新高', width: 'w-28', align: 'right', type: 'number' },
  { key: 'new_down', label: '人气排名创新低', width: 'w-28', align: 'right', type: 'number' },
  { key: 'newfans_ratio', label: '新晋粉丝占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'bigfans_ratio', label: '铁杆粉丝占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'concern_rank_7days', label: '7日关注排名', width: 'w-24', align: 'right', type: 'number' },
  { key: 'browse_rank', label: '今日浏览排名', width: 'w-24', align: 'right', type: 'number' },
  { key: 'net_inflow', label: '当日净流入', width: 'w-24', align: 'right', type: 'money' },
  { key: 'netinflow_3days', label: '3日主力净流入', width: 'w-28', align: 'right', type: 'money' },
  { key: 'netinflow_5days', label: '5日主力净流入', width: 'w-28', align: 'right', type: 'money' },
  { key: 'nowinterst_ratio', label: '当日增仓占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'nowinterst_ratio_3d', label: '3日增仓占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'nowinterst_ratio_5d', label: '5日增仓占比', width: 'w-24', align: 'right', type: 'percent' },
  { key: 'ddx', label: '当日DDX', width: 'w-18', align: 'right', type: 'number' },
  { key: 'ddx_3d', label: '3日DDX', width: 'w-16', align: 'right', type: 'number' },
  { key: 'ddx_5d', label: '5日DDX', width: 'w-16', align: 'right', type: 'number' },
  { key: 'ddx_red_10d', label: '10日内DDX飘红天数', width: 'w-32', align: 'right', type: 'number' },
  { key: 'changerate_3days', label: '3日涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'changerate_5days', label: '5日涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'changerate_10days', label: '10日涨跌幅', width: 'w-20', align: 'right', type: 'percent' },
  { key: 'changerate_ty', label: '今年以来涨跌幅', width: 'w-28', align: 'right', type: 'percent' },
  { key: 'upnday', label: '连涨天数', width: 'w-18', align: 'right', type: 'number' },
  { key: 'downnday', label: '连跌天数', width: 'w-18', align: 'right', type: 'number' },
  { key: 'listing_yield_year', label: '上市以来年化收益率', width: 'w-32', align: 'right', type: 'percent' },
  { key: 'listing_volatility_year', label: '上市以来年化波动率', width: 'w-32', align: 'right', type: 'percent' },
  { key: 'mutual_netbuy_amt', label: '沪深股通净买入', width: 'w-28', align: 'right', type: 'money' },
  { key: 'hold_ratio', label: '沪深股通持股比例', width: 'w-28', align: 'right', type: 'percent' },
];

const formatPct = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  const formatted = value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
  return formatted;
};

const formatNumber = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(0);
};

const formatMoney = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(2);
};

const formatPrice = (value: number | null): string => {
  if (value === null || value === undefined) return '-';
  return value.toFixed(2);
};

const getEastMoneyUrl = (code: string): string => {
  if (code.startsWith('6') || code.startsWith('5') || code.startsWith('9')) {
    return `https://quote.eastmoney.com/sh${code}.html`;
  } else {
    return `https://quote.eastmoney.com/sz${code}.html`;
  }
};

const getTodayIso = (): string => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

const SelectionPage: React.FC = () => {
  useEffect(() => {
    document.title = '综合选股 - STOCK';
  }, []);

  const [selectedDate, setSelectedDate] = useState(getTodayIso());
  const [stockList, setStockList] = useState<SelectionStock[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  const [sortField, setSortField] = useState<SortField>('change_rate');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  // 搜索状态
  const [searchKeyword, setSearchKeyword] = useState('');
  const [debouncedKeyword, setDebouncedKeyword] = useState('');

  const [columnFilters, setColumnFilters] = useState<Record<string, Set<string>>>({});
  const [openColumnMenu, setOpenColumnMenu] = useState<string | null>(null);
  const columnMenuRef = useRef<HTMLDivElement>(null);
  const [filteredStockList, setFilteredStockList] = useState<SelectionStock[]>([]);

  useEffect(() => {
    setFilteredStockList(stockList);
    if (currentPage > totalPages) {
      setCurrentPage(1);
    }
  }, [stockList, pageSize, totalPages]);

  const fetchSelectionData = async () => {
    setIsLoading(true);

    try {
      const params = new URLSearchParams({
        date: selectedDate,
        page: String(currentPage),
        page_size: String(pageSize),
        sort_field: sortField,
        sort_order: sortOrder,
      });
      
      Object.entries(columnFilters).forEach(([columnKey, values]) => {
        if (values && values.size > 0) {
          values.forEach(value => {
            params.append(`filters[${columnKey}]`, value);
          });
        }
      });
      
      if (debouncedKeyword.trim()) {
        params.append('keyword', debouncedKeyword.trim());
      }
      
      const url = `/api/v1/select/?${params.toString()}`;

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setStockList(result.data || []);
      setTotalCount(result.count || 0);
      setTotalPages(result.total_pages || 0);
    } catch (err) {
      console.error('获取选股数据失败:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    console.log('debounce effect triggered, searchKeyword:', searchKeyword);
    const timer = setTimeout(() => {
      console.log('debounce timeout triggered, setting debouncedKeyword:', searchKeyword);
      setDebouncedKeyword(searchKeyword);
    }, 500);

    return () => {
      console.log('debounce cleared for:', searchKeyword);
      clearTimeout(timer);
    };
  }, [searchKeyword]);

  useEffect(() => {
    setCurrentPage(1);
    void fetchSelectionData();
  }, [selectedDate, pageSize, debouncedKeyword, columnFilters]);

  useEffect(() => {
    void fetchSelectionData();
  }, [currentPage, sortField, sortOrder]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const toggleColumnFilter = (columnKey: string, value: string) => {
    setColumnFilters(prev => {
      const current = prev[columnKey] || new Set<string>();
      const newSet = new Set(current);
      if (newSet.has(value)) {
        newSet.delete(value);
      } else {
        newSet.add(value);
      }
      if (newSet.size === 0) {
        const { [columnKey]: _, ...rest } = prev;
        return rest;
      }
      return { ...prev, [columnKey]: newSet };
    });
    setCurrentPage(1);
  };

  const selectAllForColumn = (columnKey: string, allValues: string[]) => {
    setColumnFilters(prev => {
      const newSet = new Set(allValues);
      return { ...prev, [columnKey]: newSet };
    });
    setCurrentPage(1);
  };

  const clearColumnFilter = (columnKey: string) => {
    setColumnFilters(prev => {
      const { [columnKey]: _, ...rest } = prev;
      return rest;
    });
    setCurrentPage(1);
  };

  const handleColumnSort = (field: SortField, direction: 'asc' | 'desc') => {
    setSortField(field);
    setSortOrder(direction);
    setCurrentPage(1);
    setOpenColumnMenu(null);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (columnMenuRef.current && !columnMenuRef.current.contains(event.target as Node)) {
        setOpenColumnMenu(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getColumnUniqueValues = (columnKey: string): string[] => {
    const values = new Set<string>();
    stockList.forEach(stock => {
      const value = (stock as any)[columnKey];
      if (value !== null && value !== undefined) {
        values.add(String(value));
      }
    });
    return Array.from(values).sort();
  };

  const hasActiveFilter = (columnKey: string) => {
    const filter = columnFilters[columnKey];
    if (!filter || filter.size === 0) return false;
    const allValues = getColumnUniqueValues(columnKey);
    return filter.size < allValues.length;
  };

  const renderCellValue = (stock: SelectionStock, column: typeof COLUMN_CONFIG[0]) => {
    const value = (stock as any)[column.key];
    if (value === null || value === undefined) return '-';

    switch (column.type) {
      case 'price':
        return formatPrice(value);
      case 'percent':
        return formatPct(value);
      case 'money':
        return formatMoney(value);
      case 'number':
        return formatNumber(value);
      case 'flag':
        if (value === '1' || value === '是') {
          return <Badge variant="success">是</Badge>;
        } else if (value === '0' || value === '否') {
          return <Badge variant="default">否</Badge>;
        } else {
          return '-';
        }
      default:
        return String(value);
    }
  };

  const getValueColor = (value: number | null, type: string) => {
    if (type === 'percent' && value !== null) {
      if (value > 0) return 'text-red-600 dark:text-red-400';
      if (value < 0) return 'text-green-600 dark:text-green-400';
    }
    return '';
  };

  const handleExport = () => {
    const headers = COLUMN_CONFIG.map(col => col.label).join(',');
    const rows = filteredStockList.map(stock => {
      return COLUMN_CONFIG.map(col => {
        const value = (stock as any)[col.key];
        if (value === null || value === undefined) return '';
        if (typeof value === 'string' && value.includes(',')) {
          return `"${value}"`;
        }
        return String(value);
      }).join(',');
    });
    
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `selection_${selectedDate}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="limitup-page min-h-screen space-y-4 p-4 md:p-6">
      <section className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-success/10">
            <Search className="w-6 h-6 text-success" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-semibold text-foreground">综合选股</h1>
            <p className="text-xs md:text-sm text-secondary">
              根据多种指标筛选股票，支持升序降序排列和列筛选
            </p>
          </div>
        </div>

        <Card padding="md">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <label className="text-sm text-secondary">选择日期</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none"
                max={getTodayIso()}
              />
              <label className="text-sm text-secondary">关键字</label>
              <input
                type="text"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                placeholder="代码/名称/行业/概念..."
                className="input-surface input-focus-glow h-10 rounded-lg border bg-transparent px-3 text-sm transition-all focus:outline-none w-48"
              />
              {searchKeyword && (
                <button
                  type="button"
                  onClick={() => setSearchKeyword('')}
                  className="text-xs text-secondary hover:text-primary"
                >
                  清除
                </button>
              )}
            </div>
            <Badge variant="success">{totalCount} 只股票</Badge>
          </div>
        </Card>
      </section>

      <Card>
        {isLoading ? (
          <div className="flex items-center justify-center min-h-[400px] py-12">
            <Loading label="获取股票数据中..." />
          </div>
        ) : (
          <div className="relative">
            <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    {COLUMN_CONFIG.map(column => (
                      <th
                        key={column.key}
                        className={`px-3 py-3 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${column.width} ${
                          column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                        }`}
                      >
                        <div className="relative" ref={openColumnMenu === column.key ? columnMenuRef : null}>
                          <div className="flex items-center justify-center gap-1 cursor-pointer" onClick={() => setOpenColumnMenu(openColumnMenu === column.key ? null : column.key)}>
                            <span>{column.label}</span>
                            {sortField === column.key && (
                              sortOrder === 'asc' ? (
                                <ArrowUp size={14} className="text-blue-500" />
                              ) : (
                                <ArrowDown size={14} className="text-blue-500" />
                              )
                            )}
                            {hasActiveFilter(column.key) && (
                              <Filter size={12} className="text-orange-500" />
                            )}
                            <ChevronDown size={12} className={`transition-transform ${openColumnMenu === column.key ? 'rotate-180' : ''}`} />
                          </div>
                          {openColumnMenu === column.key && (
                            <div className="absolute z-50 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg" style={{ minWidth: '180px' }}>
                              <div className="py-1">
                                <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                                  排序
                                </div>
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleColumnSort(column.key as SortField, 'asc'); }}
                                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                >
                                  <ArrowUp size={14} />
                                  升序排列
                                  {sortField === column.key && sortOrder === 'asc' && <Check size={14} className="ml-auto text-blue-500" />}
                                </button>
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleColumnSort(column.key as SortField, 'desc'); }}
                                  className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                >
                                  <ArrowDown size={14} />
                                  降序排列
                                  {sortField === column.key && sortOrder === 'desc' && <Check size={14} className="ml-auto text-blue-500" />}
                                </button>
                              </div>
                              {column.type === 'flag' && (
                                <div className="py-1 border-t border-gray-200 dark:border-gray-700">
                                  <div className="px-3 py-2 text-xs text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                                    <span>筛选</span>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); selectAllForColumn(column.key, ['1', '是', '0', '否']); }}
                                      className="text-xs text-blue-500 hover:text-blue-700"
                                    >
                                      全选
                                    </button>
                                  </div>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); clearColumnFilter(column.key); }}
                                    className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <X size={14} />
                                    取消筛选
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); toggleColumnFilter(column.key, '1'); }}
                                    className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <span className={`w-4 h-4 border rounded flex items-center justify-center ${(columnFilters[column.key] || new Set()).has('1') ? 'bg-blue-500 border-blue-500' : 'border-gray-300'}`}>
                                      {(columnFilters[column.key] || new Set()).has('1') && <Check size={12} className="text-white" />}
                                    </span>
                                    显示"是"
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); toggleColumnFilter(column.key, '0'); }}
                                    className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                                  >
                                    <span className={`w-4 h-4 border rounded flex items-center justify-center ${(columnFilters[column.key] || new Set()).has('0') ? 'bg-blue-500 border-blue-500' : 'border-gray-300'}`}>
                                      {(columnFilters[column.key] || new Set()).has('0') && <Check size={12} className="text-white" />}
                                    </span>
                                    显示"否"
                                  </button>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredStockList.length === 0 ? (
                    <tr>
                      <td colSpan={COLUMN_CONFIG.length} className="px-6 py-12 text-center">
                      <EmptyState
                        title="暂无数据"
                        description="没有找到符合条件的股票数据"
                      />
                      </td>
                    </tr>
                  ) : (
                      filteredStockList.map(stock => (
                        <tr key={stock.code} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                          {COLUMN_CONFIG.map(column => (
                            <td
                              key={column.key}
                              className={`px-3 py-3 text-sm whitespace-nowrap text-gray-900 dark:text-gray-100 ${column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'} ${getValueColor((stock as any)[column.key], column.type)}`}
                            >
                              {column.key === 'code' || column.key === 'name' ? (
                                <a
                                  href={getEastMoneyUrl(stock.code)}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center gap-1"
                                >
                                  {renderCellValue(stock, column)}
                                  {column.key === 'code' && <ExternalLink size={12} />}
                                </a>
                              ) : (
                                renderCellValue(stock, column)
                              )}
                            </td>
                          ))}
                        </tr>
                      ))
                    )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>

      {filteredStockList.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mt-4 pt-4 border-t border-white/10">
              <div className="flex items-center gap-4">
                <span className="text-sm text-secondary">
                  共 {totalCount} 条记录
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-secondary">每页显示:</span>
                  <select
                    value={pageSize}
                    onChange={handlePageSizeChange}
                    className="input-surface input-focus-glow h-8 rounded border bg-transparent px-2 text-sm"
                  >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                  <span className="text-sm text-secondary">条</span>
                </div>
                <button
                  type="button"
                  onClick={handleExport}
                  className="btn-secondary h-8 px-3 flex items-center gap-2"
                >
                  <Download size={14} />
                  导出 CSV
                </button>
              </div>
              
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn-secondary h-8 px-3 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                >
                  上一页
                </button>
                
                {(() => {
                  const visiblePages = 5;
                  let start = 1;
                  
                  if (totalPages > visiblePages) {
                    if (currentPage <= 3) {
                      start = 1;
                    } else if (currentPage >= totalPages - 2) {
                      start = totalPages - 4;
                    } else {
                      start = currentPage - 2;
                    }
                  }
                  
                  const pageNumbers = [];
                  for (let i = 0; i < visiblePages && start + i <= totalPages; i++) {
                    pageNumbers.push(start + i);
                  }
                  
                  return pageNumbers.map((pageNum) => (
                    <button
                      key={pageNum}
                      type="button"
                      onClick={() => handlePageChange(pageNum)}
                      className={`h-8 w-8 px-2 rounded ${
                        currentPage === pageNum
                          ? 'bg-primary text-white'
                          : 'btn-secondary'
                      }`}
                    >
                      {pageNum}
                    </button>
                  ));
                })()}
                
                <button
                  type="button"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn-secondary h-8 px-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </div>
            </div>
          )}
    </div>
  );
};

export default SelectionPage;
