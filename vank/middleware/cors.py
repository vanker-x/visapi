from vank.core.config import conf
from vank.core.context.current import request
from vank.middleware.base import Middleware
from vank.core.http.response import ResponsePlain, Response400


class CorsMiddleware(Middleware):
    """解决跨域问题的中间件"""
    max_age: int = conf.CORS_MAX_AGE
    with_credentials: bool = conf.WITH_CREDENTIALS
    allowed_origins: list[str] = conf.CORS_ALLOWED_ORIGINS or ['*']
    allowed_methods: list[str] = conf.CORS_ALLOWED_METHODS or ['*']
    allowed_headers: list[str] = conf.CORS_ALLOWED_HEADERS or ['*']

    def __init__(self, get_response_callable):
        super().__init__(get_response_callable)
        response_headers = dict()
        # ========allowed origins========
        self.allow_all_origins = '*' in self.allowed_origins
        if self.allow_all_origins:
            response_headers['Access-Control-Allow-Origin'] = "*"
        # ========allowed origins========

        # ========allowed methods========
        if '*' in self.allowed_methods:
            self.allowed_methods = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
        response_headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
        # ========allowed methods========

        # ========allowed headers========
        self.allow_all_headers = '*' in self.allowed_headers
        if not self.allow_all_headers:
            response_headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        # ========allowed headers========
        if self.with_credentials:
            response_headers['Access-Control-Allow-Credentials'] = 'true'
        # max-age
        response_headers['Access-Control-Max-Age'] = str(self.max_age)
        self.response_headers = response_headers

    def handle_request(self):  # noqa
        # 判断请求方法是否为OPTIONS
        # 并且带有ACCESS_CONTROL_REQUEST_METHOD(接下来真正的请求会使用到哪个HTTP方法)
        # 以及ORIGIN在HTTP头部
        # 否则不处理此次请求
        if (
                not request.method == 'OPTIONS'
                and 'ACCESS_CONTROL_REQUEST_METHOD' not in request.headers
                and 'ORIGIN' not in request.headers
        ):
            return
        # 处理预检请求
        return self.handle_preflight_request(request)

    def handle_preflight_request(self, request):  # noqa
        # 处理预检请求
        origin = request.headers.get('ORIGIN')
        method = request.headers.get('ACCESS_CONTROL_REQUEST_METHOD')
        headers = request.headers.get('ACCESS_CONTROL_REQUEST_HEADERS', '')
        response_headers = dict(self.response_headers)
        failed_flag = False
        # 判断origin
        if origin not in self.allowed_origins and not self.allow_all_origins:
            failed_flag = True
        else:
            response_headers['Access-Control-Allow-Origin'] = origin
        # 预检方法
        if method.upper() not in self.allowed_methods:
            failed_flag = True
        # 判断是否有不允许的header
        if not self.allow_all_headers and headers:
            for header in headers.split(','):
                header = header.strip().lower()
                if header in self.allowed_headers:
                    continue
                failed_flag = True
                break
            else:
                # 如果都符合,那么应该返回
                response_headers['Access-Control-Allow-Headers'] = headers
        if failed_flag:
            return Response400('', headers=response_headers)
        return ResponsePlain('OK', headers=response_headers)
