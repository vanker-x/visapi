# @filename: route.py
# @Time:    2022/7/26-0:33
# @Author:  Vank
import re
from Vank.core.config import conf
from importlib import import_module
from Vank.core import exceptions


class BaseRoute:
    def __init__(self, route_path: str, methods: list, endpoint: str, *args, **kwargs):
        self.route_pattern = None
        self.route_path = route_path
        self.methods = self.__parse_methods(methods)
        self.endpoint = endpoint
        self.regex_list = []
        # 源自于werkzug.routing
        self.rule_regex_pattern = re.compile(r"""
            (?P<static_route>[^<]*)                           # 静态的路由 比如/123/<int:id> 那么 /123/就为静态路由
            <
            (?:
                (?P<converter_name>[a-zA-Z_][a-zA-Z0-9_]*)   # 转换器名字
                (?:\((?P<conv_args>.*?)\))?                  # 转换器参数
                \:                                      # 分隔符 :
            )?
            (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # 变量名字
            >
            """, re.VERBOSE)
        # 转换器类型
        self.converters = self.__load_converters()
        # 参数所对应的转换器
        self.argument_converters = {}
        # 构建正则
        self.build_rule_regex()

    def __load_converters(self):
        """
        从setting加载转换器
        """
        convters_tmp = {}
        for converter_name, converter_path in conf.ROUTE_CONVERTERS.items():
            module, cls_name = converter_path.rsplit('.', maxsplit=1)
            if converter_name in convters_tmp.keys():
                raise ValueError(f'转换器名字不能重复:{converter_name},请修改')
            convters_tmp[converter_name] = getattr(import_module(module), cls_name)()

        return convters_tmp

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

    def __parse_rule(self, path):
        """
        解析路由规则,通过regex将路由规则中的静态规则和变量规则提取出来
        :return:
        """

        if not path:
            yield None, None, None
            return

        variable_names = set()
        position = 0
        end = len(path)
        count = 0
        while position < end:
            res = self.rule_regex_pattern.match(path, position)
            if not res:
                break
            data_dic = res.groupdict()
            static_route = data_dic['static_route']
            if static_route:
                yield None, None, static_route
            variable_name = data_dic['variable']
            converter = data_dic['converter_name']
            conv_args = data_dic['conv_args']
            if not converter and variable_name:
                raise SyntaxError(f'endpoint:[{self.endpoint}]的路由参数有误:{variable_name}必须指定类型'
                                  f' <{"/".join(self.__get_converter_list())}:variable_name>')

            if variable_name in variable_names:
                raise LookupError(f'路由:{path}变量名:{variable_name}只能使用一次')
            variable_names.add(variable_name)
            yield converter, conv_args or None, variable_name
            position = res.end()
        if position < end:
            other = path[position:]
            if ">" in other or "<" in other:
                raise SyntaxError(f"{self.endpoint}存在错误的路由:{path} 不应存在:{other}")
            yield None, None, other

    def build_rule_regex(self):
        """
        创建一条属于这条路由的正则
        :return:
        """
        for converter_name, conv_args, virable_name in self.__parse_rule(self.route_path):
            if not converter_name:
                if virable_name:
                    self.regex_list.append(virable_name)
                continue
            converter = self.converters.get(converter_name)
            if not converter:
                raise LookupError(
                    f'{self.endpoint}的变量类型[{converter_name}]无法解析,'
                    f'目前支持的类型为{"/".join(self.__get_converter_list())}')
            # 将变量名对应的转换器添加到字典中,在路由过来的时候以便转换为相应的类型
            self.argument_converters.update({virable_name: converter})
            self.regex_list.append(f"(?P<{virable_name}>{converter.regex})")

        regex = f"^{''.join(self.regex_list)}$"

        self.route_pattern = re.compile(regex)
        # print(self.route_pattern)
        # print(self.endpoint)

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

    def url_for(self, endpoint: str, **arguments):
        # 根据endpoint名字反向转换为url
        if not endpoint == self.endpoint or not arguments.keys() == self.argument_converters.keys():
            raise exceptions.UrlForNotFound(endpoint,**arguments)
        route_path = self.route_path
        # 将参数转换为url
        # /<int:hello> ==>url_for(xxx,hello=1)==>/1
        for key, value in arguments.items():
            converter = self.argument_converters.get(key)
            value = converter.convert_to_url(value)
            route_path = route_path.replace(f'<{converter.name}:{key}>', value)
        return route_path

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
