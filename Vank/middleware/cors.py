# Created by Vank
# DateTime: 2022/10/9-17:33
# Encoding: UTF-8
from Vank.middleware.base import BaseMiddleware
from Vank.core.config import conf
from Vank.core.http.request import Request
import typing as t


class CorsMiddleware(BaseMiddleware):
    """解决跨域问题的中间件"""
    max_age: int = conf.CORS_MAX_AGE
    with_credentials: bool = conf.WITH_CREDENTIALS
    allowed_origins: list[str] = conf.CORS_ALLOWED_ORIGINS
    allowed_methods: list[str] = conf.CORS_ALLOWED_METHODS
    allowed_headers: list[str] = conf.CORS_ALLOWED_HEADERS

    def handle_request(self, request):
        headers = {}
        # ========allowed origins========
        if '*' in self.allowed_origins:
            headers['Access-Control-Allow-Origin'] = '*'
        # ========allowed origins========

        # ========allowed methods========
        if '*' in self.allowed_methods:
            allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
        else:
            allowed_methods = self.allowed_methods
        headers['Access-Control-Allow-Methods'] = ",".join(allowed_methods)
        # ========allowed methods========

        headers['Access-Control-Max-Age'] = str(self.max_age)

