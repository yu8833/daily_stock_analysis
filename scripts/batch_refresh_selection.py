# -*- coding: utf-8 -*-
"""
批量刷新选股数据脚本

用途：获取指定月份所有交易日的数据
用法：python scripts/batch_refresh_selection.py --year 2026 --month 5
"""

import argparse
import logging
import sys
import time
from datetime import date, timedelta

sys.path.insert(0, '/Users/yupeng/stock/daily_stock_analysis')

from src.repositories.selection_repo import SelectionRepository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def is_trading_day_2026(check_date: date) -> bool:
    """检查是否为2026年交易日（中国A股）"""
    if check_date.weekday() >= 5:
        return False

    holidays_2026 = [
        (1, 1),
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
        (10, 1), (10, 2), (10, 3), (10, 4), (10, 5), (10, 6), (10, 7),
        (4, 4), (4, 5), (4, 6),
        (6, 19), (6, 20), (6, 21),
        (9, 25), (9, 26), (9, 27),
    ]

    return (check_date.month, check_date.day) not in holidays_2026


def get_trading_days(year: int, month: int) -> list:
    """获取指定月份的所有交易日"""
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    start_date = date(year, month, 1)

    trading_days = []
    current_date = start_date

    while current_date <= end_date:
        if is_trading_day_2026(current_date):
            trading_days.append(current_date)
        current_date += timedelta(days=1)

    return trading_days


def batch_refresh(year: int, month: int, delay_seconds: float = 3.0):
    """
    批量刷新指定月份的选股数据

    Args:
        year: 年份
        month: 月份
        delay_seconds: 请求间隔时间（秒），用于避免触发东财限制
    """
    repo = SelectionRepository()
    trading_days = get_trading_days(year, month)

    logger.info(f"=== 开始批量刷新 {year}年{month:02d}月 选股数据 ===")
    logger.info(f"共 {len(trading_days)} 个交易日")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for i, trading_date in enumerate(trading_days, 1):
        logger.info(f"[{i}/{len(trading_days)}] 正在处理 {trading_date} ...")

        try:
            count = repo.save_from_fetcher(trading_date)
            if count > 0:
                logger.info(f"  ✓ 成功保存 {count} 条数据")
                success_count += 1
            else:
                logger.warning(f"  ! 未获取到数据或数据为空")
                skip_count += 1

        except Exception as e:
            logger.error(f"  ✗ 失败: {e}")
            fail_count += 1

        if i < len(trading_days):
            logger.info(f"  → 等待 {delay_seconds} 秒避免触发东财限制...")
            time.sleep(delay_seconds)

    logger.info(f"=== 批量刷新完成 ===")
    logger.info(f"成功: {success_count} 天")
    logger.info(f"失败: {fail_count} 天")
    logger.info(f"跳过: {skip_count} 天")

    return {
        'success': success_count,
        'fail': fail_count,
        'skip': skip_count,
        'total': len(trading_days)
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='批量刷新选股数据')
    parser.add_argument('--year', type=int, required=True, help='年份')
    parser.add_argument('--month', type=int, required=True, help='月份')
    parser.add_argument('--delay', type=float, default=3.0, help='请求间隔（秒），默认3秒')

    args = parser.parse_args()

    batch_refresh(args.year, args.month, args.delay)
