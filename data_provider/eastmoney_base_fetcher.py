# -*- coding: utf-8 -*-
"""
===================================
EastmoneyBaseFetcher - 东方财富基础获取器
===================================

提供统一的东方财富网数据获取基础功能
"""

import os
import random
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class EastmoneyBaseFetcher:
    """
    东方财富网基础数据获取器
    
    封装了Cookie管理、会话管理和请求发送功能
    """
    
    def __init__(self):
        self.session = self._create_session()
    
    def _get_cookie(self):
        """
        获取东方财富网的Cookie
        优先级：环境变量 > 文件 > 默认Cookie
        """
        cookie = os.environ.get('EAST_MONEY_COOKIE')
        if cookie:
            return cookie
        
        cookie_file = Path('config/eastmoney_cookie.txt')
        if cookie_file.exists():
            with open(cookie_file, 'r') as f:
                cookie = f.read().strip()
            if cookie:
                return cookie
        
        return 'st_si=78948464251292; st_psi=20260205091253851-119144370567-1089607836; st_pvi=07789985376191; st_sp=2026-02-05%2009%3A11%3A13; st_inirUrl=https%3A%2F%2Fxuangu.eastmoney.com%2FResult; st_sn=12; st_asi=20260205091253851-119144370567-1089607836-webznxg.dbssk.qxg-1'
    
    def _create_session(self):
        """创建并配置会话"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,
            pool_maxsize=50
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://data.eastmoney.com/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        session.headers.update(headers)
        
        cookie = self._get_cookie()
        if cookie:
            session.headers['Cookie'] = cookie
        
        return session
    
    def make_request(self, url, params=None, retry=3, timeout=15):
        """
        发送请求
        """
        for i in range(retry):
            try:
                time.sleep(random.uniform(1, 2))
                
                response = self.session.get(
                    url,
                    params=params,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"请求错误: {e}, 第 {i + 1}/{retry} 次重试")
                if i < retry - 1:
                    time.sleep(random.uniform(2, 4))
                else:
                    raise