import inspect
import typing as t
from vank.core import exceptions
from vank.core.routing.route import Route
from vank.core.context.current import request
from vank.core.view import View
from vank.utils.arguments import contain_arguments, has_key_word_argument

HTTP_METHOD_TYPE = t.Literal["GET", "POST", "PUT", "DELETE", "HEAD", "PATCH", "OPTIONS", "TRACE"]
ViewType = t.TypeVar("ViewType", callable, View)


class Router:
    def __init__(self):
        self._routes = []
        self.route_path_set = set()
        # endpoint -->view_func 映射
        self.endpoint_func_dic = {}

    def match(self):
        """
        需要检查请求方法,需要
        :return:
        """

        for route in self._routes:
            # 遍历路由列表并匹配
            res = route.route_pattern.match(request.path)
            if not res:
                continue
            # 判断请求方法是否允许
            if not route.check_method(request.method):
                raise exceptions.MethodNotAllowedException(f'"{request.method.upper()}" Method is not allowed',
                                                           allow=route.methods)
            # 获取endpoint和类型转换后的参数
            endpoint, arguments = route.endpoint, route.convert_arguments(**res.groupdict())
            view_function = self.endpoint_func_dic.get(endpoint)
            return view_function, arguments

        # 如果路由规则都没有找到那么就报404错误
        raise exceptions.NotFoundException(f'Resource {request.path} not found')

    @property
    def routes(self):
        for route in self._routes:
            yield route

    def include_router(self, router: "Router"):
        """
        此方法应该由主应用(Application)调用 目的是为了将子应用(SubApplication)的路由注册到主应用中
        """
        # 遍历子路由的所有路由
        for route in router.routes:
            # 获取路由未构建时的路径
            route_path = route.route_path
            # 获取视图函数
            callback = router.endpoint_func_dic.get(route.endpoint)
            self.route_path_set.add(route_path)
            self._routes.append(route)
            self.endpoint_func_dic[route.endpoint] = callback

    def url_reflect(self, endpoint: str, **arguments):
        for route in self.routes:
            try:
                return route.url_reflect(endpoint, **arguments)
            except exceptions.ReflectNotFound:
                pass
        raise exceptions.ReflectNotFound(endpoint, **arguments)

    def adapt_view_func(self, callback: ViewType, methods):
        # 利用inspect 检查是否为类或者函数
        if inspect.isclass(callback) and issubclass(callback, View):  # noqa
            # 当视图为 View 视图的子类时 methods 应该为None
            if methods is not None:
                raise ValueError(f'The methods parameter should not be passed in when using class view {callback}')
            view = callback()
            methods_list = view.get_view_methods
        elif inspect.isfunction(callback):
            view = callback
            methods_list = methods
        else:
            raise ValueError(
                f'View-function should be a function or subclass of "View" instead of {type(callback).__name__}')

        return view, methods_list

    def check_view_parameters(self):
        pass

    def route(
            self,
            route_path: str,
            methods: t.Optional[t.List[HTTP_METHOD_TYPE]] = None,
            endpoint: t.Optional[str] = None
    ):
        def inner(callback: ViewType):
            # route_path必须以/开头
            assert route_path.startswith(
                '/'), f'The route "{route_path}" of the {callback!r} view should start with "/"'
            ep = endpoint or callback.__name__
            # 不能存在两个相同的路由路径
            if route_path in self.route_path_set:
                raise ValueError('"%s" This route path is already in the router.' % route_path)
            # 不能存在相同的endpoint
            if self.endpoint_func_dic.get(ep, None):
                raise ValueError('"%s" This endpoint is already in the router.' % ep)
            # 适配类视图和函数视图
            callback, method_list = self.adapt_view_func(callback, methods)
            route = Route(route_path, methods, endpoint=ep)
            if (
                    not contain_arguments(callback, route.argument_converters.keys())
                    and
                    not has_key_word_argument(callback)
            ):
                raise ValueError(
                    f"You should provide positional parameters such as {','.join(route.argument_converters.keys())}."
                    f" or provide a keyword variable parameter to the view function '{callback.__name__}'")
            self.route_path_set.add(route_path)
            self._routes.append(route)
            self.endpoint_func_dic[ep] = callback

            return callback

        return inner

    def get(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["GET"], endpoint=endpoint)

    def post(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["POST"], endpoint=endpoint)

    def put(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["PUT"], endpoint=endpoint)

    def delete(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["DELETE"], endpoint=endpoint)

    def head(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["HEAD"], endpoint=endpoint)

    def patch(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["PATCH"], endpoint=endpoint)

    def options(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["OPTIONS"], endpoint=endpoint)

    def trace(self, route_path: str, endpoint: t.Optional[str] = None):
        return self.route(route_path, methods=["TRACE"], endpoint=endpoint)

    def __str__(self):
        return '\n'.join(
            '{route} <==> {view_func}'
            .format(route=route, view_func=self.endpoint_func_dic.get(route.endpoint))
            for route in self.routes
        )

    def __repr__(self):
        return '\n'.join(
            '{route} <==> {view_func}'
            .format(route=route, view_func=self.endpoint_func_dic.get(route.endpoint))
            for route in self.routes
        )
