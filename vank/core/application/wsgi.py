import typing as t
from vank.core import conf
from vank.core import exceptions
from wsgiref.simple_server import make_server
from vank.core.context.base import auto_reset
from vank.core.http.request import WSGIRequest
from vank.core.http.response import BaseResponse
from vank.core.application.base import MiddlewareAppMixin
from vank.core.context.current import application, request
from vank.core.routing.router import Router, RouteNotFound
from vank.utils.locator import get_obj_file
from vank.utils.reloader import run_in_reloader
from vank.utils.signal import on_request_start, on_request_end


class WSGIApplication(MiddlewareAppMixin, Router):

    def __init__(self):
        MiddlewareAppMixin.__init__(self)
        Router.__init__(self)

    def start(self):
        def inner():
            httpd = make_server(conf.DEFAULT_HOST, conf.DEFAULT_PORT, self)
            httpd.serve_forever()

        if conf.AUTO_RELOAD:
            run_in_reloader(inner, conf.AUTO_RELOAD_INTERVAL)
        else:
            inner()

    def finalize(self, *args, **kwargs):
        """
        handle process the final callback
        :param args: middlewares may pass in some args.
        :param kwargs: middlewares may pass in some keyword args.
        :return: Response
        """
        try:
            route, route_kwargs = self.match(request.path, protocol=self.route_cls.protocol)
        except RouteNotFound as e:
            raise exceptions.NotFoundException(f'"{request.path}" is not found')
        if not route.check_method(request.method):
            raise exceptions.MethodNotAllowedException(
                f'{request.method} method is not allowed',
                allow=route.methods
            )
        converted = route.convert_arguments(**route_kwargs)
        kwargs.update(converted)
        response = route.callback(*args, **kwargs)
        if not isinstance(response, BaseResponse):
            raise exceptions.NoResponseException(
                f'The callback "{route.callback}" '
                f'at file "{get_obj_file(route.callback)}" did not return a response'
            )
        return response

    def _finish_response(self, response: BaseResponse, start_response: callable) -> t.Iterable[bytes]:
        """
        处理response 调用start_response设置响应状态码和响应头
        :param response: 封装的response 详情请看Vank/core/http/response
        :param start_response: WSGI规范的start_response
        :return: Iterable[bytes] 返回的body数据
        """
        # 默认的output的header参数是”Set-Cookie:“
        # 我们只需要后面的值而不需要”Set-Cookie:“
        # 所以应该将header行参设置为空
        headers = response.headers.items()
        # 设置cookie
        headers.extend([("Set-Cookie", cookie.output(header="")) for cookie in response.cookies.values()])
        start_response(response.status, headers)
        return response

    @auto_reset(lambda self, *args, **kwargs: (application._wrapped.set(self), application))  # noqa
    @auto_reset(lambda self, environ, start_response: (request._wrapped.set(WSGIRequest(environ)), request))  # noqa
    def __call__(self, environ: dict, start_response: callable):
        """
        This is WSGI application entrypoint
        :param environ: dictionary of enviroment
        :param start_response: call to send response
        :return: Iter[bytes]
        """
        # 请求开始信号
        on_request_start.emit(self)
        response = self.entry_point()
        on_request_end.emit(self, response=response)
        request.close()
        return self._finish_response(response, start_response)
