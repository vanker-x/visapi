from typing import List
from .http import request
from .handlers import exception
from .route.route_map import Route_Map
from .route.router import Route

__version__ = '0.1.0'


class App:
    def __init__(self):
        # 将项目settings加入system的path
        self.route_map = Route_Map()
        self.endpoint_func_dic = {}
        self.error_handler = exception.default_handler

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

    def new_route(self, route_path: str, methods=List[str], **kwargs):
        def decorator(view_func: callable):
            # 判断是否可调用
            assert callable(view_func), f'路由"{route_path}"所装饰的对象不可调用'
            # 判断路由是否以/开头
            assert route_path.startswith('/'), f'{view_func.__name__}视图的路由"{route_path}"应该以/开头'
            # 调用set_route方法
            self.__set_route(route_path, view_func, methods, **kwargs)

        return decorator

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

    def __process_response(self, response, startResponse) -> List[bytes]:
        """
        处理response 将response的状态码,header存入startResponse
        并返回一个二进制列表
        :param response: 封装的response 详情请看Vank/core/http/response
        :param startResponse: wsgiref提供的startresponse
        :return: list[bytes] 返回的body数据
        """
        startResponse(response.status_code, list(response.header.items()))
        return [response.data]

    def __call__(self, environ, startResponse):
        """

        :param environ:环境变量以及请求参数等
        :param startResponse:wsgi提供的一个function 我们需要给他设置响应码以及响应头等信息
        :return:list[bytes]一个二进制列表 作为响应数据
        """
        Request = request.Request(environ)
        # 全局的错误捕获
        try:
            func, view_args = self.__dispatch_route(Request)
            Response = func(Request, **view_args)
        except Exception as exc:
            Response = self.error_handler(Request, exc)

        return self.__process_response(Response, startResponse)
