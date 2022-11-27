from uuid import UUID
from abc import ABCMeta, abstractmethod

"""
这个模块 将路由字符串转换为对应的Python Object 或者 将Python Object 转换为url
例如 一个路由为 /<int:number> 且一个请求的路径字符串为 /123
那么 请求路径后的数字 123 会有str 类型转换为 int 类型 并以名为number的变量 进入对应的处理函数
所以 对应的处理函数应该提供一个number位置参数
"""


class BasicConverter(metaclass=ABCMeta):
    regex = None

    @abstractmethod
    def convert_to_python(self, value):
        """
        将 value 转换为python Object 此方法应由子类完成
        :param value: 需要被转换为Python Object的值
        :return:
        """
        pass

    @abstractmethod
    def convert_to_url(self, value):
        """
        将Python Object 转换为 url  此方法应由子类完成
        :param value: Python Object
        :return:
        """
        pass


# 数字转换器
class IntConverter(BasicConverter):
    regex = r"\d+"

    def convert_to_python(self, value):
        return int(value)

    def convert_to_url(self, value):
        return str(value)


# 字符串转换器
class StrConverter(BasicConverter):
    regex = r'[^/]+'

    def convert_to_python(self, value):
        return str(value)

    def convert_to_url(self, value):
        return str(value)


# 浮点数转换器
class FloatConverter(BasicConverter):
    regex = r"[0-9]+(.[0-9]+)?"

    def convert_to_python(self, value):
        return float(value)

    def convert_to_url(self, value):
        return str(value)


# 邮箱转换器
class EmailConverter(BasicConverter):
    regex = r'[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+'

    def convert_to_python(self, value):
        return str(value)

    def convert_to_url(self, value):
        return str(value)


# UUID转换器
class UUIDConverter(BasicConverter):
    regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    def convert_to_python(self, value):
        return UUID(value)

    def convert_to_url(self, value):
        return str(value)


class PathConverter(BasicConverter):
    regex = '.*'

    def convert_to_python(self, value):
        return str(value)

    def convert_to_url(self, value):
        return str(value)
