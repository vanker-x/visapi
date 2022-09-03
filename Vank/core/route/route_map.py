from Vank.core.route.router import Route
from Vank.core import exceptions


class Route_Map:
    def __init__(self):
        self.route_list = []
        self.route_path_set = set()

    def add_route(self, route_path: str, route: "Route"):
        '''
        添加路由到路由列表中 同时校验是否有相同路由
        '''
        if route_path in self.route_path_set:
            raise LookupError(f'不能同时存在相同路由:[{route_path}]')

        self.route_path_set.add(route_path)
        self.route_list.append(route)

    def match(self, request):
        """
        需要检查请求方法,需要
        :param request:
        :return:
        """

        for route in self.route_list:
            # 遍历路由列表并匹配
            res = route.route_pattern.match(request.path)
            if not res:
                continue
            # 判断请求方法是否允许
            if not route.check_method(request.method):
                raise exceptions.MethodNotAllowedException(f'{request.method.upper()}方法不被允许')
            # 获取endpoint和类型转换后的参数
            endpoint, arguments = route.endpoint, route.convert_arguments(**res.groupdict())
            return endpoint, arguments

        # 如果路由规则都没有找到那么就报404错误
        raise exceptions.NotFoundException
