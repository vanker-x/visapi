from Vank.core import exceptions
from Vank.core.routing.route import Route


class Router:
    def __init__(self):
        self._routes = []
        self.route_path_set = set()
        # endpoint -->view_func 映射
        self.endpoint_func_dic = {}

    def add_route(self, route_path: str, route: "Route", view_func):
        """
        添加路由到路由列表中 同时校验是否有相同路由
        """
        if route_path in self.route_path_set:
            raise LookupError(f'不能同时存在相同路由:[{route_path}]')

        self.route_path_set.add(route_path)
        self._routes.append(route)
        # 判断是否有相同的endpoint且该endpoint应该指向同一视图函数 否则报错
        endpoint = route.endpoint
        exist_func = self.endpoint_func_dic.get(endpoint, None)
        if exist_func and view_func is not exist_func:
            raise ValueError(f'一个endpoint不应指向多个视图:[{endpoint}]')
        self.endpoint_func_dic[endpoint] = view_func

    def match(self, request):
        """
        需要检查请求方法,需要
        :param request:
        :return:
        """

        for route in self._routes:
            # 遍历路由列表并匹配
            res = route.route_pattern.match(request.path)
            if not res:
                continue
            # 判断请求方法是否允许
            if not route.check_method(request.method):
                raise exceptions.MethodNotAllowedException(f'{request.method.upper()}方法不被允许', allow=route.methods)
            # 获取endpoint和类型转换后的参数
            endpoint, arguments = route.endpoint, route.convert_arguments(**res.groupdict())
            view_function = self.endpoint_func_dic.get(endpoint)
            return view_function, arguments

        # 如果路由规则都没有找到那么就报404错误
        raise exceptions.NotFoundException(f'资源 {request.path} 未找到')

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
            view_func = router.endpoint_func_dic.get(route.endpoint)
            # 添加到主路由中
            self.add_route(route_path, route, view_func)

    def url_for(self, endpoint: str, **arguments):
        for route in self.routes:
            try:
                return route.url_for(endpoint, **arguments)
            except exceptions.UrlForNotFound:
                pass
        raise exceptions.UrlForNotFound(endpoint, **arguments)

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
