# Created by Vank
# DateTime: 2022/9/26-17:16
# Encoding: UTF-8
from functools import cached_property
from Vank.core.exceptions import NoneViewMethodException


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
            raise NoneViewMethodException('类视图应至少定义一个http请求方法所对应的类方法')
        return allowed_methods

    def __call__(self, request, *args, **kwargs):
        """
        视图的入口
        """
        request_method: str = request.method
        return getattr(self, request_method.lower())(request, *args, **kwargs)

    @property
    def __name__(self):
        return self.__class__.__name__
