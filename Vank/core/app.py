from typing import List
from types import FunctionType
from Vank.core.config import conf
from Vank.core.views.view import View
from Vank.utils import import_from_str
from Vank.core.route.router import Route
from Vank.core.route.route_map import Route_Map
from Vank.core.exceptions import NonResponseException
from Vank.core.handlers.exception import conv_exc_to_response
from Vank.core.http import (
    request as req,
    response as rep
)

__version__ = '0.1.0'


class App:
    def __init__(self):
        # 实例化路由映射表
        self.route_map = Route_Map()
        self.endpoint_func_dic = {}
        # 获取error_handler 捕获全局错误
        self.error_handler = import_from_str(conf.ERROR_HANDLER)
        # 初始化视图中间件列表
        self.__handle_view_middlewares = []
        # 初始化中间件
        self.initial_middlewares()

    def initial_middlewares(self):
        """
        初始化中间件 接收到的请求将会传入self.middlewares进行处理
        当配置文件中没有中间件时 self.middlewares 为 conv_exc_to_response
        :return:
        """
        # 将实例方法 get_response 包裹在全局异常处理转换器中
        get_response_func = conv_exc_to_response(self.__get_response, self.error_handler)

        for m_str in conf.MIDDLEWARES:
            # 导入中间件类
            middleware_class = import_from_str(m_str)
            # 实例化中间件 将handler传入其中
            middleware_instance = middleware_class(get_response_func)

            if not middleware_instance:
                raise RuntimeError(f'初始化中间件错误,{middleware_instance} 中间件不应该为空')

            # 如果该中间件有handle_view方法 那么就添加到__handle_view_middlewares中
            if hasattr(middleware_instance, 'handle_view'):
                self.__handle_view_middlewares.append(middleware_instance.handle_view)
            # 将中间件包裹在全局异常处理转换器中
            get_response_func = conv_exc_to_response(middleware_instance, self.error_handler)

        # 形成一个中间件链
        self.middlewares = get_response_func

    def __get_response(self, request):
        """
        获取response  如果任意一个中间件定义了 handle_view方法  该方法会调用调用handle_view
        如果 所有的handle_view返回值都是None 那么 请求会进入 对应的视图函数

        当 视图函数返回一个非 BaseResponse 或 BaseResponse子类实例时
        raise NonResponseException

        :param request:
        :return:
        """
        response = None
        # 获取到对应的处理试图和该试图所需的参数
        view_func, view_kwargs = self.__dispatch_route(request)

        for view_handle in self.__handle_view_middlewares:
            response = view_handle(request, view_func, **view_kwargs)
            if response:
                break

        # 如果handle_view 没有返回response 那么就交给视图函数处理
        if not response:
            response = view_func(request, **view_kwargs)
        # 当视图返回的不是BaseResponse 或 BaseResponse子类的实例 raise NonResponseException
        if not isinstance(response, rep.BaseResponse):
            raise NonResponseException("服务未返回任何数据")

        return response

    def __set_route(self, route_path, view_func, methods, *args, **kwargs):
        '''
        添加路由
        '''
        # 获取endpoint
        endpoint = view_func.__name__ if not kwargs.get('endpoint') else kwargs.pop('endpoint')
        # 实例化一个路由
        route = Route(route_path, methods, endpoint, **kwargs)
        # 添加到路由映射表中
        self.route_map.add_route(route_path, route)
        # 判断是否有相同的endpoint 如果有则报错
        func = self.endpoint_func_dic.get(endpoint)
        if func and not view_func == func:
            raise ValueError(f'不能同时存在相同的endpoint:[{endpoint}]')

        self.endpoint_func_dic.update({
            endpoint: view_func
        })

    def new_route(self, route_path: str, methods=None, **kwargs):
        def decorator(func_or_class):
            # 判断是否为类视图
            if hasattr(func_or_class, 'get_view_methods') and issubclass(func_or_class, View):
                view = func_or_class()
                methods_list = view.get_view_methods
            elif isinstance(func_or_class, FunctionType):
                view = func_or_class
                methods_list = methods
            else:
                raise Exception(f'{func_or_class}视图应该为一个函数或View的子类')
            # 判断路由是否以/开头
            assert route_path.startswith('/'), f'{view.__name__}视图的路由"{route_path}"应该以/开头'
            # 调用set_route方法
            self.__set_route(route_path, view, methods_list, **kwargs)

        return decorator

    def add_route(self, route_path: str, methods: List[str], view_func, **kwargs):
        assert callable(view_func), 'view_func 必须为可调用对象'
        assert route_path.startswith('/'), f'{view_func.__name__}视图的路由"{route_path}"应该以/开头'
        self.__set_route(route_path, view_func, methods, **kwargs)
        return self

    def start(self, host: str = 'localhost', port: int = 8000):
        """
        开启服务
        :param host: 主机地址
        :param port: 服务端口
        :return: None
        """
        assert self.endpoint_func_dic, '未能找到至少一个以上的视图处理请求'
        from wsgiref.simple_server import make_server
        tip = f"""Vank {__version__} 已开启 该服务仅用于开发模式,切勿用于生产环境 生产环境请由WSGI服务器开启 例如uwsgi、gunicorn
服务地址:http://{host}:{port}/"""
        print(tip)
        make_server(host, port, self).serve_forever()

    def __dispatch_route(self, request):
        """
        根据请求信息找到处理该url的视图函数
        :param request:封装的request请求实例 详情请看Vank/core/http/request
        :return:一个视图函数
        """
        endpoint, view_kwargs = self.route_map.match(request)
        view_function = self.endpoint_func_dic[endpoint]

        return view_function, view_kwargs

    def _finish_response(self, response, startResponse) -> List[bytes]:
        """
        处理response 调用start_response设置响应状态码和响应头
        并返回一个二进制列表
        :param response: 封装的response 详情请看Vank/core/http/response
        :param startResponse: wsgiref提供的startresponse
        :return: list[bytes] 返回的body数据
        """
        startResponse(response.status, list(response.header.items()))
        return [response.data]

    def __call__(self, environ, startResponse):
        """
        被WSGI Server调用
        :param environ:环境变量以及请求参数等
        :param startResponse:wsgi提供的一个function 我们需要给他设置响应码以及响应头等信息
        :return:list[bytes]一个二进制列表 作为响应数据
        """
        request = req.Request(environ)
        response = self.middlewares(request)

        return self._finish_response(response, startResponse)
