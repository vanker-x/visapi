import typing as t

if t.TYPE_CHECKING:
    from visapi.app import VisAPI


class RSGIHandler:
    def __init__(self, app: "VisAPI"):
        self.app = app

    async def handle(self, scope, protocol):
        raise NotImplementedError

    async def __call__(self, scope, protocol):
        return await self.handle(scope, protocol)


class HTTPHandler(RSGIHandler):
    async def handle(self, scope, protocol):
        pass


class WebsocketHandler(RSGIHandler):
    async def handle(self, scope, protocol):
        pass
