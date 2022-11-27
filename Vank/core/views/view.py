# Created by Vank
# DateTime: 2022/9/26-17:16
# Encoding: UTF-8
from functools import cached_property
from Vank.core.config import conf
from Vank.middleware.base import BaseMiddleware
from Vank.core.http.response import BaseResponse
from Vank.core.exceptions import NoneViewMethodException, NonResponseException
from Vank.core.handlers.exception import conv_exc_to_response


class View:
    """
    通过类构建http请求方法对应类方法的视图
    子类至少实现一个http方法对应的类方法 否则会引发NoneViewMethodException异常
    例如:
     def get(self, request, *args, **kwargs):
         ...
         return Response

     def post(self, request, *args, **kwargs):
         ...
         return Response

    """

    @cached_property
    def get_view_methods(self):
        http_methods = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
        allowed_methods = [method for method in http_methods if hasattr(self, method)]
        if not allowed_methods:
            raise NoneViewMethodException('类视图应至少定义一个http请求方法所对应的方法')
        return allowed_methods

    def get_response(self, request, *args, **kwargs):
        request_method: str = request.method
        return getattr(self, request_method.lower())(request, *args, **kwargs)

    def __call__(self, request, *args, **kwargs):
        """
        视图的入口
        """
        return self.get_response(request, *args, **kwargs)

    @property
    def __name__(self):
        return self.__class__.__name__


class MiddlewareView(View):
    """
    中间件视图
    例如:
    class Demo(MiddlewareView):
        middlewares = [CustomMiddleware,]
        error_handler = default_handler
        force_handle_request = False

        def get(self,request,*args,**kwargs):
            return Response
    """
    middlewares = []
    error_handler = conf.ERROR_HANDLER
    force_handle_request = False  # 强制执行handle_request

    def __init__(self):
        if not self.middlewares:
            raise ValueError
        self.entry_func = None
        self.handle_view_middlewares = []
        self.setup()

    def setup(self):
        self.entry_func = conv_exc_to_response(self.get_response, self.error_handler)
        for middleware_class in self.middlewares:
            if not issubclass(middleware_class, BaseMiddleware):
                raise TypeError(f'{middleware_class}必须为BaseMiddleware的子类')

            if not self.force_handle_request and hasattr(middleware_class, 'handle_request'):
                delattr(middleware_class, 'handle_request')

            # 实例化中间件
            middleware_instance = middleware_class(self.entry_func)

            # 判断是否有handle_view方法,有则添加到handle_view_middlewares中
            if hasattr(middleware_instance, 'handle_view'):
                self.handle_view_middlewares.append(middleware_instance.handle_view)
            self.entry_func = conv_exc_to_response(middleware_instance, self.error_handler)

    def __call__(self, request, *args, **kwargs):
        response = self.entry_func(request, *args, **kwargs)
        if not isinstance(response, BaseResponse):
            raise NonResponseException('服务应返回一个Response实例')
        return response
