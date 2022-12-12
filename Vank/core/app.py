import inspect
import logging
from typing import List, Optional, Union
from Vank.core.config import conf
from Vank.core.views.view import View
from Vank.core.views.static import StaticView
from Vank.utils import import_from_str
from Vank.utils.log import setup_config as setup_log_config
from Vank.core.routing.route import Route
from Vank.core.routing.router import Router
from Vank.core.exceptions import NonResponseException
from Vank.core.handlers.exception import conv_exc_to_response
from Vank.core.http import (request as req, response as rep)
from Vank.utils.reloader import run_in_reloader

__version__ = '0.1.0'
logger = logging.getLogger('console')


class Base:
    def __init__(self):
        # 实例化路由映射表
        self.router = Router()

    def __set_route(self, route_path, view_func, methods, **kwargs):
        """
        添加路由
        """
        assert route_path.startswith('/'), f'{view_func} 视图的路由"{route_path}"应该以/开头'
        # 获取endpoint
        endpoint = kwargs.pop('endpoint', None) or view_func.__name__
        # 判断本实例是否为子应用,那么就应该加上子应用名字
        if isinstance(self, SubApplication):
            endpoint = f'{self.name}.{endpoint}'
        # 实例化一个路由
        route = Route(route_path, methods, endpoint, **kwargs)
        # 添加到路由映射表中
        self.router.add_route(route_path, route, view_func)

    def adapt_view_func(self, func_or_class, methods):
        # 利用inspect 检查是否为类或者函数
        if inspect.isclass(func_or_class) and issubclass(func_or_class, View):
            # 当视图为 View 视图的子类时 methods 应该为None
            if methods is not None:
                raise ValueError(f'使用类视图 {func_or_class} 不应传入methods 参数')
            view = func_or_class()
            methods_list = view.get_view_methods
        elif inspect.isfunction(func_or_class):
            view = func_or_class
            methods_list = methods
        else:
            raise ValueError(f'视图应该为一个函数或View的子类 而不是{func_or_class}')

        return view, methods_list

    def new_route(self, route_path: str, methods=None, **kwargs):
        def decorator(func_or_class):
            view, methods_list = self.adapt_view_func(func_or_class, methods)
            # 调用set_route方法
            self.__set_route(route_path, view, methods_list, **kwargs)
            return func_or_class

        return decorator

    def get(self, route_path, **kwargs):
        """
        注册视图允许的请求方法仅为get的快捷方式
        """
        return self.new_route(route_path, ['GET'], **kwargs)

    def post(self, route_path, **kwargs):
        """
        注册视图允许的请求方法仅为post的快捷方式
        """
        return self.new_route(route_path, ['POST'], **kwargs)

    def put(self, route_path, **kwargs):
        """
        注册视图允许的请求方法仅为put的快捷方式
        """
        return self.new_route(route_path, ['PUT'], **kwargs)

    def patch(self, route_path, **kwargs):
        """
        注册视图允许的请求方法仅为patch的快捷方式
        """
        return self.new_route(route_path, ['PATCH'], **kwargs)

    def delete(self, route_path, **kwargs):
        """
        注册视图允许的请求方法仅为delete的快捷方式
        """
        return self.new_route(route_path, ['DELETE'], **kwargs)

    def add_route(self, route_path: str, func_or_class, methods=None, **kwargs):
        self.new_route(route_path, methods, **kwargs)(func_or_class)
        return self


class Application(Base):
    def __init__(self):
        super(Application, self).__init__()
        # 获取error_handler 捕获全局错误
        self.error_handler = import_from_str(conf.ERROR_HANDLER)
        # 初始化视图中间件列表
        self.__handle_view_middlewares = []
        # 请求的入口函数
        self.entry_func = None
        self._setup()

    def _setup(self):
        # 配置logging
        setup_log_config(conf.LOGGING)
        self.new_route(conf.STATIC_URL + '<path:fp>', endpoint='static')(StaticView)
        # 初始化中间件
        self.initial_middleware_stack()

    def initial_middleware_stack(self):
        """
        初始化中间件 接收到的请求将会传入self.middlewares进行处理
        当配置文件中没有中间件时 self.middlewares 为 conv_exc_to_response
        :return:
        """
        # 将实例方法 get_response 包裹在全局异常处理转换器中
        get_response_func = conv_exc_to_response(self.__get_response, self.error_handler)

        for m_str in reversed(conf.MIDDLEWARES):
            # 导入中间件类
            middleware_class = import_from_str(m_str)
            # 实例化中间件 将handler传入其中
            middleware_instance = middleware_class(get_response_func)

            if not middleware_instance:
                raise RuntimeError(f'初始化中间件错误,{middleware_instance} 中间件不应该为空')

            # 如果该中间件有handle_view方法 那么就添加到__handle_view_middlewares中
            if hasattr(middleware_instance, 'handle_view'):
                self.__handle_view_middlewares.insert(0, middleware_instance.handle_view)
            # 将中间件包裹在全局异常处理转换器中
            get_response_func = conv_exc_to_response(middleware_instance, self.error_handler)

        # 形成一个中间件栈
        self.entry_func = get_response_func

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

        handle_view_middlewares = self.__handle_view_middlewares.copy()
        # 判断视图函数是否有handle_view_middlewares 方法 有则extend到全局的handle_view_middlewares中
        if hasattr(view_func, 'handle_view_middlewares'):
            handle_view_middlewares.extend(getattr(view_func, 'handle_view_middlewares'))
        # 执行handle_view
        for view_handler in handle_view_middlewares:
            response = view_handler(request, view_func, **view_kwargs)
            if response:
                break

        # 如果handle_view 没有返回response 那么就交给视图函数处理
        if not response:
            response = view_func(request, **view_kwargs)
        # 当视图返回的不是BaseResponse 或 BaseResponse子类的实例 raise NonResponseException
        if not isinstance(response, rep.BaseResponse):
            raise NonResponseException("服务应返回一个Response实例")

        return response

    def start(self):
        """
        开启服务
        :return: None
        """
        assert self.router.endpoint_func_dic, '未能找到至少一个以上的视图处理请求'

        # 判断是否使用热重载
        if conf.AUTO_RELOAD:
            run_in_reloader(
                self._inner_run,
                conf.AUTO_RELOAD_INTERVAL,
                conf.AUTO_RELOAD_SPEC_SUFFIX,
                conf.AUTO_RELOAD_IGNORE_SUFFIX
            )
        else:
            self._inner_run()

    def _inner_run(self):
        from wsgiref.simple_server import make_server
        # if os.environ.get('autoreload', None):
        #     logger.warning(f"你的服务运行于:http://{conf.DEFAULT_HOST}:{conf.DEFAULT_PORT}/"
        #                    f"这只适用于开发环境,请勿用于生产环境;"
        #                    f"请使用gunicorn、uwsgi等wsgi服务器启动")
        logger.warning(f"你的服务运行于:http://{conf.DEFAULT_HOST}:{conf.DEFAULT_PORT}/"
                       f"这只适用于开发环境,请勿用于生产环境;"
                       f"请使用gunicorn、uwsgi等wsgi服务器启动")
        httpd = make_server(conf.DEFAULT_HOST, conf.DEFAULT_PORT, self)
        httpd.serve_forever()

    def include(self, sub: Union[str, "SubApplication"]):
        """
        将子应用挂载到Application中,类似Flask的register_blueprint
        """
        if isinstance(sub, str):
            sub = import_from_str(sub)
        if not isinstance(sub, SubApplication):
            raise TypeError(f"参数 sub类型不应该为{type(sub)}")
        self.router.include_router(sub.router)

    def __dispatch_route(self, request):
        """
        根据请求信息找到处理该url的视图函数
        :param request:封装的request请求实例 详情请看Vank/core/http/request
        :return:一个视图函数
        """
        view_function, view_kwargs = self.router.match(request)
        return view_function, view_kwargs

    def _finish_response(self, response, start_response) -> List[bytes]:
        """
        处理response 调用start_response设置响应状态码和响应头
        并返回一个二进制列表
        :param response: 封装的response 详情请看Vank/core/http/response
        :param start_response: WSGI规范的start_response
        :return: list[bytes] 返回的body数据
        """
        start_response(response.status, list(response.header.items()))
        return [response.data]

    def __call__(self, environ, start_response) -> List[bytes]:
        """
        被WSGI Server调用
        :param environ:环境变量以及请求参数等
        :param start_response:WSGI规范的一个function 我们需要给他设置响应码以及响应头等信息
        :return:作为响应数据
        """
        request = req.Request(environ)
        response = self.entry_func(request)

        return self._finish_response(response, start_response)


class SubApplication(Base):
    def __init__(self, name, prefix: Optional[str] = None):
        super(SubApplication, self).__init__()
        self.name = name
        self.prefix = prefix
        if self.prefix:
            assert not self.prefix.endswith('/'), "url前缀不应以 '/'结尾"
            assert self.prefix.startswith('/'), "url前缀应以 '/'开头"

    def new_route(self, route_path: str, methods=None, **kwargs):
        if self.prefix:
            assert route_path.startswith("/"), f'子应用{self.name}视图的路由"{route_path}"应该以/开头'
            route_path = self.prefix + route_path
        return super(SubApplication, self).new_route(route_path, methods, **kwargs)
