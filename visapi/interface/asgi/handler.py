import asyncio
import typing as t

from visapi.exceptions import HTTPException
from visapi.interface.asgi.http import Request
from visapi.interface.asgi.websocket import Websocket

if t.TYPE_CHECKING:
    from visapi.app import VisAPI


class ASGIHandler:
    def __init__(self, app: "VisAPI"):
        self.app = app

    async def handle(self, scope, receive, send):
        raise NotImplementedError

    async def __call__(self, scope, receive, send):
        try:
            return await self.handle(scope, receive, send)
        except Exception as e:
            self.app.error_handler.handle(e)
        finally:
            pass


class HTTPHandler(ASGIHandler):
    async def handle(self, scope, receive, send):
        request = Request(scope, receive, send)
        handler = self.app.router(request.path, method=request.method.upper(), protocol="http")
        await handler()


class WebsocketHandler(ASGIHandler):
    async def handle(self, scope, receive, send):
        websocket = Websocket(scope, receive, send)
        handler = self.app.router(websocket.path, protocol="websocket")


class LifeSpanHandler(ASGIHandler):
    async def handle(self, scope, receive, send):
        pass
