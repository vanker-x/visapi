import re
import typing as t
from urllib.parse import quote
from functools import lru_cache
from vank.core import exceptions
from vank.core.config import conf
from vank.types import HTTPMethod
from vank.utils.locator import get_obj_file
from vank.utils.load_module import import_from_str

# 构建路由正则
build_route_regex_pattern = re.compile(
    "(?P<static_route>[^{]*){(?P<variable>[a-zA-Z_][a-zA-Z0-9_]*):(?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)}"
)


def parse_route_path(route_path: str):
    """
    Yield a tuple containing static part,variable name and converter name,
    and finally yield the remaining part
    :param route_path: route path rule
    :return:
    """
    start = 0
    end = len(route_path)
    while start < end:
        # 通过语法正则匹配出动态路由
        res = build_route_regex_pattern.search(route_path, start)
        # 如果没有匹配出结果、说明剩余的字符串是静态的
        if not res:
            break
        group_dict = res.groupdict()
        yield group_dict["static_route"], group_dict["variable"], group_dict["converter"]
        start = res.end()
    # 拼接剩余静态路由
    if start < end:
        legacy_route = route_path[start:]
        if '{' in legacy_route or '}' in legacy_route:
            raise SyntaxError('Incorrect routing syntax.Should not appear single "{" or "}"')
        yield legacy_route, None, None


@lru_cache(maxsize=None)
def get_converters() -> dict:
    """
    Get a dict of converters
    :return: dict of converters
    """
    convert_dict = dict()
    for converter_name, convert_module_path in conf.ROUTE_CONVERTERS.items():
        if converter_name in convert_dict.keys():
            raise ValueError(f'The converter name "{converter_name}" cannot be duplicate')
        converter_class = import_from_str(convert_module_path)
        convert_dict[converter_name] = converter_class()
    return convert_dict


class BaseRoute:
    protocol: str = None

    def __init__(self, route_path: str, endpoint: str, callback: callable):
        self.callback = callback
        self.endpoint = endpoint
        self.route_pattern = None  # 解析后的路由规则
        self.route_path = route_path  # 用户定义的路由规则
        self.regex_list = []
        self.converters = get_converters()
        self.argument_converters = {}
        self.setup()

    def setup(self):
        """
        Build a regular object based on route path rule
        :return:
        """
        for static_route, variable, converter_name in parse_route_path(self.route_path):
            # 需要将静态路径escape防止出现转义安全问题
            # 例如 直接拼接'/foo.bar'这段规则到路由正则中，那么匹配'/fooobar'也能通过匹配,这是不合法的
            self.regex_list.append(re.escape(static_route))
            # ===处理动态路由===
            if converter_name is None:
                continue
            if variable in self.argument_converters.keys():
                raise SyntaxError(f"Duplicate keyword parameters '{variable}' cannot appear in same route path")
            converter = self.converters.get(converter_name, None)
            if converter is None:
                raise SyntaxError(f" Converter '{converter_name}' does not exist.")
            # 将变量名对应的转换器添加到字典中,在路由过来的时候以便转换为相应的类型
            self.argument_converters.update({variable: converter})
            self.regex_list.append(f"(?P<{variable}>{converter.regex})")
        # 开始拼接解析后的路由规则
        regex = f"^{''.join(self.regex_list)}$"

        self.route_pattern = re.compile(regex)

    def get_converter_list(self):
        """
        Get a list of all converter keys
        :return: list of converter keys
        """
        return list(self.converters.keys())

    def convert_arguments(self, **arguments):
        """
        Convert the string to the corresponding type through the corresponding converter
        :param arguments:
        :return: converted arguments
        """
        for arg_name, arg_value in arguments.items():
            new_value = self.argument_converters[arg_name].convert_to_python(arg_value)
            arguments.update({arg_name: new_value})
        return arguments

    def url_reflect(self, endpoint: str, **arguments):
        """
        Find the corresponding routing rule based on the endpoint,
        and construct a URL string where arguments must be a superset of the required parameters
        for the corresponding routing rule.and any excess parameters will be concatenated into the query parameters
        :param endpoint:
        :param arguments:
        :return:
        """
        # 根据endpoint反向构建url、并且传入的arguments必须为该路由所需的可变路由参数的超集
        if not endpoint == self.endpoint or not set(arguments.keys()).issuperset(self.argument_converters.keys()):
            raise exceptions.ReflectNotFound(endpoint, **arguments)
        url = self.route_path
        # 将传入的arguments替换为url、甚于的参数作为查询参数
        for variable_name, converter in self.argument_converters.items():
            value = converter.convert_to_url(arguments.pop(variable_name))
            raw_rule = '{%(variable_name)s:%(converter_name)s}' % dict(
                variable_name=variable_name,
                converter_name=converter.name
            )
            url = url.replace(raw_rule, value)
        query_args = "&".join([f"{key}={value}" for key, value in arguments.items()])
        if query_args:
            url = url + f"?{query_args}"
        # 为了解决URL规范问题需要对route_path进行quote
        # safe参数指的是不对safe的值进行转换
        return quote(url, safe="/#%[]=:;$&()+,!?*@'~")

    def __str__(self):
        return '<{cls_name}>: "{route_path}" <=> "{endpoint}" <=> {callback} <=> {file_at}'.format(
            route_path=self.route_path,
            cls_name=self.__class__.__name__,
            regex=self.route_pattern,
            endpoint=self.endpoint,
            callback=self.callback,
            file_at=get_obj_file(self.callback),
        )

    def __repr__(self):
        return '<{cls_name}>: "{route_path}" <=> "{endpoint}" <=> {callback} <=> {file_at}'.format(
            route_path=self.route_path,
            cls_name=self.__class__.__name__,
            regex=self.route_pattern,
            endpoint=self.endpoint,
            callback=self.callback,
            file_at=get_obj_file(self.callback),
        )


class Route(BaseRoute):
    protocol = "http"

    def __init__(self, route_path: str, methods: t.List[HTTPMethod], endpoint: str, callback: callable):
        super(Route, self).__init__(route_path, endpoint, callback)
        self.methods = methods

    def check_method(self, method: HTTPMethod) -> bool:
        """
        Determine whether the route allows this method
        :param method: http request method
        :return: boolean value
        """
        return method.upper() in self.methods


class WebsocketRoute(BaseRoute):
    protocol = "websocket"

    def __init__(self, route_path: str, endpoint: str, callback: callable):
        super().__init__(route_path, endpoint, callback)
