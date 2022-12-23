from Vank.core.http import HTTP_Status
from Vank.core.http import response
from Vank.core.exceptions import *
from Vank.utils.exception import get_exception_reason
from logging import getLogger

logger = getLogger()


def conv_exc_to_response(get_response_func, error_handler):
    """
    全局的捕获异常,将异常转换为对应的response
    :param get_response_func: 获取reponse的函数 当存在中间件时 该参数为上一个中间件 不存在时 为 APP实例下的__get_response方法
    :param error_handler: 处理错误的处理器
    :return:
    """

    def inner(request, *args, **kwargs):
        try:
            return get_response_func(request, *args, **kwargs)
        except Exception as e:
            return error_handler(request, e)

    return inner


def default_handler(request, exc):
    """
    错误处理器 根据对应的错误返回对应的Response 如果未找到对应错误 默认返回 Response 500
    :param request: request对象
    :param exc: Exception对象
    :return: Response
    """
    logger.error("", exc_info=exc)
    if isinstance(exc, NotFoundException):
        return response.Response404()

    if isinstance(exc, MethodNotAllowedException):
        return response.Response405(exc.allow)

    if isinstance(exc, PermissionDeniedException):
        return response.Response403()

    return response.Response500()
