from Vank.core.routing.route import Route
from Vank.core import exceptions


class Router:
    def __init__(self):
        self._routes = []
        self.route_path_set = set()
        # endpoint 字典
        self.endpoint_func_dic = {}

    def add_route(self, route_path: str, route: "Route", view_func):
        """
        添加路由到路由列表中 同时校验是否有相同路由
        """
        if route_path in self.route_path_set:
            raise LookupError(f'不能同时存在相同路由:[{route_path}]')

        self.route_path_set.add(route_path)
        self._routes.append(route)
        # 判断是否有相同的endpoint 否则报错
        endpoint = route.endpoint
        exist_func = self.endpoint_func_dic.get(endpoint, None)
        if exist_func and view_func is not exist_func:
            raise ValueError(f'不能同时存在相同的endpoint:[{endpoint}]')
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
                raise exceptions.MethodNotAllowedException(f'{request.method.upper()}方法不被允许')
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
        for route in router.routes:
            route_path = route.route_path
            view_func = router.endpoint_func_dic.get(route.endpoint)
            self.add_route(route_path, route, view_func)
