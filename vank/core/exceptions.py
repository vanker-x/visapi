# @filename: exceptions.py
# @Time:    2022/7/26-1:40
# @Author:  vank

class ReflectNotFound(Exception):
    def __init__(self, endpoint, **arguments):
        super(ReflectNotFound, self).__init__(f'URL reflect did not find the corresponding path'
                                              f' <{endpoint}><==>{"".join(arguments.keys())}')


class NotFoundException(Exception):
    """资源未找到错误"""


class MethodNotAllowedException(Exception):
    def __init__(self, msg, allow, *args):
        self.allow = allow
        super(MethodNotAllowedException, self).__init__(msg, *args)

    """请求方法不允许错误"""


class PermissionDeniedException(Exception):
    """权限错误"""


class NoResponseException(Exception):
    """视图未返回Response"""


class NoneViewMethodException(Exception):
    """类视图未定义至少一个类方法"""
