from logging import getLogger
from vank.core.exceptions import *
from vank.core.http import response
from vank.utils.coroutine_function import is_coroutine_function

logger = getLogger('server')


def conv_exc_to_response(fn, exception_converter):
    """
    Global exception catcher, which can convert exceptions into response objects.
    :param fn: the callable object wrapped by the catcher
    :param exception_converter: converter for converting exception
    :return: response
    """

    def inner(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return exception_converter(e)

    async def ainner(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            return exception_converter(e)

    return ainner if is_coroutine_function(fn) else inner


def default_exception_converter(exc):
    """
    The exception converter returns exception-based response, and
    if an unexpected exception is received, a 500 response will be returned
    :param exc: exception
    :return: response
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
