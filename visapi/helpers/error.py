import typing as t
from weakref import WeakValueDictionary


class ErrorHandler:
    def __init__(self, app):
        self.app = app
        self.handlers = WeakValueDictionary()

    def add_error_handler(self, exception, handler):
        if exception in self.handlers:
            raise ValueError(f"Duplicate error handler found :{exception}")
        self.handlers[exception] = handler

    def on_error(self, exception: BaseException):
        def inner(handler: t.Callable):
            return self.add_error_handler(exception, handler)

        return inner

    async def handle(self, exception):
        # exclude “object” ancestor
        for cls in exception.__class__.__mro__[:-1]:
            if handler := self.handlers.get(cls):
                return await handler(exception)
        return await self.default(exception)

    async def default(self, exception):
        return exception
