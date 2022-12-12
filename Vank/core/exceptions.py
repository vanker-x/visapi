# @filename: exceptions.py
# @Time:    2022/7/26-1:40
# @Author:  Vank
from Vank.core.http import status


class UrlForNotFound(Exception):
    def __init__(self, endpoint, **arguments):
        super(UrlForNotFound, self).__init__(f'url_for未找到对应的路径 <{endpoint}><==>{"".join(arguments.keys())}')


class NotFoundException(Exception):
    """资源未找到错误"""


class MethodNotAllowedException(Exception):
    """请求方法不允许错误"""


class PermissionDeniedException(Exception):
    """权限错误"""


class NonResponseException(Exception):
    """视图未返回Response"""


class NoneViewMethodException(Exception):
    """类视图未定义至少一个类方法"""
