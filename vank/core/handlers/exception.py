from vank.core.http import response
from vank.core.exceptions import *
from logging import getLogger

logger = getLogger('server')


def conv_exc_to_response(get_response_func, error_handler):
    """
    全局的捕获异常,将异常转换为对应的response
    :param get_response_func: 获取reponse的函数 当存在中间件时 该参数为上一个中间件 不存在时 为 APP实例下的__get_response方法
    :param error_handler: 处理错误的处理器
    :return:
    """

    def inner(*args, **kwargs):
        try:
            return get_response_func(*args, **kwargs)
        except Exception as e:
            return error_handler(e)

    return inner


def default_handler(exc):
    """
    错误处理器 根据对应的错误返回对应的Response 如果未找到对应错误 默认返回 Response 500
    :param exc: Exception对象
    :return: Response
    """
    if isinstance(exc, NotFoundException):
        resp = response.Response404()
    elif isinstance(exc, MethodNotAllowedException):
        resp = response.Response405(exc.allow)
    elif isinstance(exc, PermissionDeniedException):
        resp = response.Response403()
    else:
        resp = response.Response500()
    logger.error("Error - ", exc_info=exc)
    return resp
