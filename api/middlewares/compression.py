# -*- coding: utf-8 -*-
"""
===================================
压缩中间件
===================================

职责：
1. 提供Gzip压缩响应
2. 自动检测Accept-Encoding头
3. 根据响应大小决定是否压缩
"""

import gzip
import io
import logging
from typing import Callable, Optional, Tuple, Union
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)


class GzipMiddleware(BaseHTTPMiddleware):
    """Gzip压缩中间件"""
    
    def __init__(
        self,
        app: FastAPI,
        minimum_size: int = 1024,  # 1KB以下不压缩
        compress_level: int = 6
    ):
        """
        初始化压缩中间件
        
        Args:
            app: FastAPI应用
            minimum_size: 最小压缩大小（字节）
            compress_level: 压缩级别（1-9）
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compress_level = compress_level
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 检查是否需要压缩
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # 检查Content-Type是否适合压缩
        content_type = response.headers.get("content-type", "")
        if not self._should_compress_content_type(content_type):
            return response
        
        # 获取响应体
        if hasattr(response, "body_iterator"):
            return response
        
        response_body = b""
        if hasattr(response, "body"):
            response_body = response.body
        else:
            async for chunk in response.body_iterator:
                response_body += chunk
        
        # 检查响应大小
        if len(response_body) < self.minimum_size:
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # 压缩响应
        compressed_body = self._compress(response_body)
        
        # 创建压缩响应
        headers = dict(response.headers)
        headers["Content-Encoding"] = "gzip"
        headers["Content-Length"] = str(len(compressed_body))
        headers.pop("Vary", None)
        headers["Vary"] = "Accept-Encoding"
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )
    
    def _should_compress_content_type(self, content_type: str) -> bool:
        """
        判断内容类型是否需要压缩
        
        Args:
            content_type: Content-Type
            
        Returns:
            是否需要压缩
        """
        content_type = content_type.lower()
        
        # 适合压缩的内容类型
        compressible_types = [
            "text/",
            "application/json",
            "application/javascript",
            "application/x-javascript",
            "text/javascript",
            "text/css",
            "application/xml",
            "text/xml",
            "application/xhtml+xml",
            "image/svg+xml",
        ]
        
        # 不适合压缩的类型
        not_compressible_types = [
            "image/",
            "video/",
            "audio/",
            "application/zip",
            "application/gzip",
            "application/pdf",
        ]
        
        for t in not_compressible_types:
            if content_type.startswith(t):
                return False
        
        for t in compressible_types:
            if content_type.startswith(t):
                return True
        
        return False
    
    def _compress(self, data: bytes) -> bytes:
        """
        压缩数据
        
        Args:
            data: 原始数据
            
        Returns:
            压缩后的数据
        """
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=self.compress_level) as f:
            f.write(data)
        return buffer.getvalue()
