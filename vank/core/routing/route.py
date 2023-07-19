# @filename: route.py
# @Time:    2022/7/26-0:33
# @Author:  vank
import re
from urllib.parse import quote
from vank.core.config import conf
from vank.core import exceptions
from vank.utils.load_module import import_from_str
from functools import lru_cache

# 构建路由正则
build_route_regex_pattern = re.compile(
    "(?P<static_route>[^{]*){(?P<variable>[a-zA-Z_][a-zA-Z0-9_]*):(?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)}"
)


def parse_route_rule(rule):
    start = 0
    end = len(rule)
    while start < end:
        # 通过语法正则匹配出动态路由
        res = build_route_regex_pattern.search(rule, start)
        # 如果没有匹配出结果、说明剩余的字符串是静态的
        if not res:
            break
        result_dict = res.groupdict()
        static_route = result_dict.get("static_route")
        variable = result_dict.get("variable")
        converter = result_dict.get("converter")
        if result_dict.get("static_route"):
            yield None, static_route
        yield converter, variable
        start = res.end()
    # 拼接剩余静态路由
    if start < end:
        legacy_route = rule[start:]
        if '{' in legacy_route or '}' in legacy_route:
            raise SyntaxError('错误的路由语法')
        yield None, legacy_route


@lru_cache(maxsize=None)
def get_converters():
    """
    获取路由转换器
    """
    convert_dict = dict()
    for converter_name, convert_module_path in conf.ROUTE_CONVERTERS.items():
        if converter_name in convert_dict.keys():
            raise ValueError(f'转换器名字不能重复:{converter_name},请修改')
        converter_class = import_from_str(convert_module_path)
        convert_dict[converter_name] = converter_class()
    return convert_dict


class BaseRoute:
    def __init__(self, route_path: str, methods: list, endpoint: str, *args, **kwargs):
        self.route_pattern = None  # 解析后的路由规则
        self.route_path = route_path  # 用户定义的路由规则
        self.methods = self.__parse_methods(methods)  # 路由的method
        self.endpoint = endpoint  # 端点
        self.regex_list = []
        # 转换器类型
        self.converters = get_converters()
        # 参数所对应的转换器
        self.argument_converters = {}
        # 构建正则
        self.setup()

    def __parse_methods(self, methods: list):
        if not methods:
            return ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"]
        methods_upper = [method.upper() for method in methods]
        if not set(methods_upper) < {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS", "TRACE"}:
            raise ValueError(f'{self.endpoint}定义路由请求方法时出错,存在非HTTP请求方法')
        return methods_upper

    def __get_converter_list(self):
        """
        获取所有转换器的列表
        """
        return self.converters.keys()

    def setup(self):
        """
        创建一条属于这条路由的正则
        :return:
        """
        for converter_name, static_or_variable in parse_route_rule(self.route_path):
            # 没有路由转换器,但是static_or_variable不为空、则可以判定static_or_variable为静态的路由
            if not converter_name and static_or_variable:
                # 需要将静态路径escape防止出现安全问题
                # 例如 '/foo.bar' 如果直接append那么如果访问/fooobar也是能够访问到此条路由，这是不合法的
                self.regex_list.append(re.escape(static_or_variable))
                continue
            # ===处理动态路由===
            if static_or_variable in self.argument_converters.keys():
                raise SyntaxError('路由规则中不能出现重复的关键字参数')
            converter = self.converters.get(converter_name)
            if not converter:
                raise SyntaxError(
                    f'{self.endpoint}的变量对应转换器[{converter_name}]未找到,'
                    f'目前支持的类型为{"、".join(self.__get_converter_list())}')
            # 将变量名对应的转换器添加到字典中,在路由过来的时候以便转换为相应的类型
            self.argument_converters.update({static_or_variable: converter})
            self.regex_list.append(f"(?P<{static_or_variable}>{converter.regex})")
        # 开始拼接解析后的路由规则
        regex = f"^{''.join(self.regex_list)}$"

        self.route_pattern = re.compile(regex)

    def convert_arguments(self, **arguments):
        """
        将变量转换为对应的类型
        例如:将整数字符串转换为int类型
        """
        for arg_name, arg_value in arguments.items():
            new_value = self.argument_converters[arg_name].convert_to_python(arg_value)
            arguments.update({arg_name: new_value})
        return arguments


class Route(BaseRoute):
    def __init__(self, route_path, methods, endpoint, *args, **kwargs):
        super(Route, self).__init__(route_path, methods, endpoint, *args, **kwargs)

    def check_method(self, request_method):
        return request_method.upper() in self.methods

    def url_reflect(self, endpoint: str, **arguments):
        """
        根据endpoint查找对应的url
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
        return '<{cls_name}>:{regex} <==> {endpoint}'.format(
            cls_name=self.__class__.__name__,
            regex=self.route_pattern,
            endpoint=self.endpoint
        )

    def __repr__(self):
        return '<{cls_name}>:{regex} <==> {endpoint}'.format(
            cls_name=self.__class__.__name__,
            regex=self.route_pattern,
            endpoint=self.endpoint
        )
