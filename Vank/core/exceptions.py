# @filename: exceptions.py
# @Time:    2022/7/26-1:40
# @Author:  Vank
from Vank.core.http import status

class BasicException(Exception):
    def __init__(self):
        self.code = status.HTTP_400_BAD_REQUEST


class NotFoundException(BasicException):
    def __init__(self, description='资源未找到或请求路径有误'):
        self.code = status.HTTP_404_NOT_FOUND
        self.description = description

    def __str__(self):
        return 'Not Found Exception'


class MethodNotAllowedException(BasicException):
    def __init__(self, description='方法不被允许'):
        self.code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.description = description

    def __str__(self):
        return 'MethodNotAllowedException'


class A(BasicException):
    def __init__(self, description=''):
        self.code = status.HTTP_404_NOT_FOUND
        self.description = description

    def __str__(self):
        return
