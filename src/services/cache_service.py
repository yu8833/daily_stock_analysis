# -*- coding: utf-8 -*-
"""
===================================
缓存服务模块
===================================

职责：
1. 提供内存缓存服务（LRU Cache）
2. 支持TTL（Time To Live）过期机制
3. 线程安全的缓存操作
"""

import logging
import threading
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Callable, Optional, TypeVar, Tuple, Dict
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TTLCache:
    """带过期时间的LRU缓存"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒）
        """
        self._cache: OrderedDict[str, Tuple[Any, datetime]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        
    def _is_expired(self, expire_time: datetime) -> bool:
        """检查是否过期"""
        return datetime.now() > expire_time
    
    def _evict_expired(self):
        """清理过期条目"""
        expired_keys = []
        for key, (_, expire_time) in self._cache.items():
            if self._is_expired(expire_time):
                expired_keys.append(key)
            else:
                break
        
        for key in expired_keys:
            del self._cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在或过期返回None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expire_time = self._cache[key]
            if self._is_expired(expire_time):
                del self._cache[key]
                return None
            
            self._cache.move_to_end(key)
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认使用default_ttl
        """
        with self._lock:
            if ttl is None:
                ttl = self._default_ttl
            
            expire_time = datetime.now() + timedelta(seconds=ttl)
            
            if key in self._cache:
                self._cache.move_to_end(key)
            elif len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = (value, expire_time)
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def __contains__(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        return self.get(key) is not None


class CacheManager:
    """缓存管理器，管理多个缓存实例"""
    
    _instance: Optional['CacheManager'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._caches: Dict[str, TTLCache] = {}
        self._lock = threading.RLock()
    
    def get_cache(self, name: str, max_size: int = 1000, default_ttl: int = 300) -> TTLCache:
        """
        获取或创建缓存实例
        
        Args:
            name: 缓存名称
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒）
            
        Returns:
            缓存实例
        """
        with self._lock:
            if name not in self._caches:
                self._caches[name] = TTLCache(max_size=max_size, default_ttl=default_ttl)
            return self._caches[name]
    
    def clear_all(self) -> None:
        """清空所有缓存"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()


_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """获取缓存管理器单例"""
    return _cache_manager


def cached(name: str = "default", key_func: Optional[Callable[..., str]] = None, ttl: int = 300):
    """
    缓存装饰器
    
    Args:
        name: 缓存名称
        key_func: 键生成函数，默认使用位置参数的str()连接
        ttl: 过期时间（秒）
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache = _cache_manager.get_cache(name, default_ttl=ttl)
            
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key_parts = [str(arg) for arg in args]
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key = "|".join(key_parts)
            
            result = cache.get(key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl)
            return result
        
        return wrapper
    return decorator
