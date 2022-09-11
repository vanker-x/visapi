from Vank.core.http.status import *
from Vank.core.http.response import Response
from Vank.core.exceptions import *


def conv_exc_to_response(get_response_func, error_handler):
    """
    全局的捕获异常,将异常转换为对应的response
    :param get_response_func: 获取reponse的函数 当存在中间件时 该参数为上一个中间件 不存在时 为 APP实例下的__get_response方法
    :param error_handler: 处理错误的处理器
    :return:
    """

    def inner(request):
        try:
            return get_response_func(request)
        except Exception as e:
            return error_handler(request, e)

    return inner


def default_handler(request, exec):
    if isinstance(exec, NotFoundException):
        errors = {
            'error': exec.description
        }
        return Response(request, errors, status=HTTP_404_NOT_FOUND)

    if isinstance(exec, MethodNotAllowedException):
        errors = {
            'error': exec.description
        }
        return Response(request, errors, status=HTTP_405_METHOD_NOT_ALLOWED)

    return Response(request, '服务器发生了错误', status=HTTP_500_INTERNAL_SERVER_ERROR)
