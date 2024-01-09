import typing as t
from vank.core import exceptions
from vank.types import HTTPMethod
from vank.core.routing.route import Route
from vank.utils.arguments import accept_arguments, accept_var_key_word_argument


class RouteNotFound(Exception):
    pass


class Router:
    route_cls = Route

    def __init__(self):
        # 存放路由实例
        self._routes = []
        # 防止多次注册同一个路由规则
        self.named_path_set = set()
        self.endpoint_set = set()

    def match(self, path: str, protocol: t.Optional[str] = "all") -> t.Tuple[Route, t.Dict]:
        """
        Process the incoming path string to sequentially match the routing instance and return a tuple.
        and RouteNotFound exception if it is not matched
        :param protocol: Specify a protocol to match this protocol of route and default is all
        :param path: Possible matching strings
        :return: The first is the route instance, and the second is the unconverted keyword-arguments dict
        of the routing rule
        """
        # Match a routing instance that matches the path
        for route in self._routes:
            res = route.route_pattern.match(path)
            if not res:
                continue
            if protocol == 'all' or route.protocol == protocol:
                return route, res.groupdict()
        raise RouteNotFound(f'No route can fit this path "{path}"')

    @property
    def routes(self):
        """
        Return all routing instances
        :return:
        """
        return self._routes

    def include_router(self, router: "Router"):
        """
        You can expand other routers based on this method
        :param router:
        :return:
        """
        pass

    def url_reflect(self, endpoint: str, **arguments):
        """
        Reflect as a quoted URL path based on the provided endpoint
        :param endpoint:  for target callback
        :param arguments: keyword routing parameters required by the target routing rule,
         and additional parameters that you can provide as query parameters
        :return:
        """
        if endpoint not in self.endpoint_set:
            raise exceptions.ReflectNotFound(endpoint, **arguments)
        for route in self.routes:
            try:
                return route.url_reflect(endpoint, **arguments)
            except exceptions.ReflectNotFound:
                pass
        raise exceptions.ReflectNotFound(endpoint, **arguments)

    def _validate_parameter(self, callback, parameters):
        if (
                not accept_arguments(callback, parameters)
                and
                not accept_var_key_word_argument(callback)
        ):
            raise ValueError(
                f"You should provide positional parameters such as {','.join(parameters)}."
                f" or provide a keyword variable parameter to the callback function '{callback.__name__}'")

    def _validate_route_param(self, route_path: str, endpoint: str, callback: callable, protocol: t.Optional[str] = ""):
        # The route path must start with /
        assert route_path.startswith(
            '/'), f'The route "{route_path}" of the {callback!r} callback should start with "/"'
        # enable to solve different protocol can not appear same route path
        named_path = f"{protocol}:{route_path}"
        if named_path in self.named_path_set:
            raise ValueError('"%s" This route path is already in the router.' % route_path)
        self.named_path_set.add(named_path)
        if endpoint in self.endpoint_set:
            ValueError('"%s" This endpoint is already in the router.' % endpoint)
        self.endpoint_set.add(endpoint)

    def route(
            self,
            route_path: str,
            methods: t.List[HTTPMethod],
            endpoint: t.Optional[str] = None,
    ):
        """
        This is a decorator, you can register the route to the router
        :param route_path: route path rule
        :param methods: allowed HTTP methods
        :param endpoint: you can understand it as a namespace, and default is callback name
        :return: callback this method decorated
        """
        def inner(callback: callable):
            ep = endpoint or callback.__name__
            self._validate_route_param(route_path, ep, callback, protocol=self.route_cls.protocol)
            route = self.route_cls(
                route_path=route_path,
                methods=methods,
                endpoint=ep,
                callback=callback)
            self._validate_parameter(callback, route.argument_converters.keys())
            self._routes.append(route)
            return callback

        return inner

    def get(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the GET method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["GET"], endpoint=endpoint)

    def post(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the POST method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["POST"], endpoint=endpoint)

    def put(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the PUT method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["PUT"], endpoint=endpoint)

    def delete(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the DELETE method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["DELETE"], endpoint=endpoint)

    def head(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the HEAD method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["HEAD"], endpoint=endpoint)

    def patch(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the PATCH method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["PATCH"], endpoint=endpoint)

    def options(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the OPTIONS method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["OPTIONS"], endpoint=endpoint)

    def trace(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        Shortcut to register the TRACE method
        :param route_path: route path rule
        :param endpoint: endpoint for callback
        :return:
        """
        return self.route(route_path, methods=["TRACE"], endpoint=endpoint)

    def __str__(self):
        return '\n'.join('{route}'.format(route=route) for route in self.routes)

    def __repr__(self):
        return '\n'.join('{route}'.format(route=route) for route in self.routes)
