import inspect
import typing as t

import asgiref.sync

from vank.core import exceptions
from vank.utils.coroutine_function import is_coroutine_function
from vank.utils.locator import get_obj_file
from vank.core.context.base import auto_reset
from vank.core.http.request import ASGIRequest
from vank.core.http.websocket import WebSocket
from vank.core.http.response import Response
from vank.core.routing.route import WebsocketRoute
from vank.core.application.base import MiddlewareAppMixin
from vank.core.routing.router import Router, RouteNotFound
from vank.core.context.current import application, websocket, request

if t.TYPE_CHECKING:
    from contextvars import Token
    from vank.core.context.base import ContextProxy


def set_websocket_ctx(
        self,
        scope,
        receive,
        send
) -> t.Union[t.Tuple[None, None], t.Tuple["Token", "ContextProxy"]]:
    """
    Setup websocket global context var
    :param self: application
    :param scope: Which is a dict containing details about the specific connection.
    :param receive: An asynchronous callable which lets the application receive event messages from the client
    :param send: An asynchronous callable, that lets the application send event messages to the client.
    :return:
    """
    if not scope["type"] == "websocket":  # do not set websocket ctx var
        return None, None
    return websocket._wrapped.set(WebSocket(scope, receive, send)), websocket  # noqa


def set_request_ctx(
        self,
        scope,
        receive,
        send
) -> t.Union[t.Tuple[None, None], t.Tuple["Token", "ContextProxy"]]:
    """
    Setup request global context var
    :param self: application
    :param scope: Which is a dict containing details about the specific connection.
    :param receive: An asynchronous callable which lets the application receive event messages from the client
    :param send: An asynchronous callable, that lets the application send event messages to the client.
    :return:
    """
    if not scope["type"] == "http":  # do not set request ctx var
        return None, None
    return request._wrapped.set(ASGIRequest(scope, receive)), request  # noqa


class ASGIApplication(MiddlewareAppMixin, Router):
    ws_route_cls = WebsocketRoute

    def __init__(self):
        MiddlewareAppMixin.__init__(self)
        Router.__init__(self)

    async def finalize(self, *args, **kwargs):
        """
        This method always sits at the bottom of the middleware stack and
        is always wrapped by an exception handler to better handle routing matching.
        :param args: the previous calls may have passed something in.
        :param kwargs: the previous calls may have passed some keyword arguments in.
        :return: response
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
        if is_coroutine_function(route.callback):
            callback = route.callback
        else:
            callback = asgiref.sync.sync_to_async(route.callback)
        response = await callback(*args, **kwargs)
        if not isinstance(response, Response):
            raise exceptions.NoResponseException(
                f'The callback "{route.callback}" '
                f'at file "{get_obj_file(route.callback)}" did not return a response'
            )
        return response

    def ws(self, route_path: str, endpoint: t.Optional[str] = None):
        """
        This is a decorator, you can register the websocket route to the router, and
        the callback must be coroutine function.
        :param route_path: route path rule
        :param endpoint: same as route method
        :return: callback this method decorated
        """

        def inner(callback: callable):
            if not inspect.iscoroutinefunction(callback):
                raise TypeError("websocket callback must be coroutine function")
            ep = endpoint or callback.__name__
            self._validate_route_param(route_path, ep, callback, protocol=self.ws_route_cls.protocol)
            route = self.ws_route_cls(route_path=route_path, endpoint=ep, callback=callback)
            self._validate_parameter(callback, route.argument_converters.keys())
            self._routes.append(route)
            return callback

        return inner

    async def _finish_response(self, response, send):
        """
        Handle finish response
        :param response:
        :param send:
        :return:
        """
        # TODO adapt response
        await send({
            'type': "http.response.start",
            "status": response.status,
        })
        async for body in response:
            await send({
                'type': "http.response.body",
                'body': body
            })

    @auto_reset(lambda self, *args, **kwargs: (application._wrapped.set(self), application))  # noqa
    @auto_reset(set_websocket_ctx)
    @auto_reset(set_request_ctx)
    async def __call__(self, scope, receive, send):
        """
        This is ASGI application entrypoint
        :param scope: which is a dict containing details about the specific connection.
        :param receive: an asynchronous callable which lets the application receive event messages from the client
        :param send: an asynchronous callable, that lets the application send event messages to the client.
        :return:
        """
        scope_type = scope["type"]
        if scope_type == "lifespan":
            return

        if scope_type == "http":
            response = await self.entry_point()
            await self._finish_response(response, send)
            request.close()
            return
        elif scope["type"] == "websocket":
            # TODO Remove explicit parameter websocket
            websocket = WebSocket(scope, receive, send)
            try:
                route, route_kwargs = self.match(websocket.path, protocol=self.ws_route_cls.protocol)
            except RouteNotFound as e:
                await websocket.close()
                return
            converted = route.convert_arguments(**route_kwargs)
            try:
                await route.callback(websocket, **converted)
            except Exception as e:
                if not websocket.is_closed:
                    await websocket.close()
        else:
            raise ValueError(f"unsupported scope tpye {scope_type}")
