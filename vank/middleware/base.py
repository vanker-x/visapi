import asgiref.sync
from vank.utils import coroutine_function


class Middleware:
    def __init__(self, next_):
        self.next = next_
        if coroutine_function.is_coroutine_function(self.next):
            coroutine_function.mark_coroutine_function(self)

    def handle(self, *args, **kwargs):
        response = None
        # 处理请求
        if hasattr(self, 'handle_request'):
            response = self.handle_request()
        # 交给对应的函数处理
        if not response:
            response = self.next(*args, **kwargs)

        # 处理response
        if hasattr(self, 'handle_response'):
            response = self.handle_response(response)

        return response

    async def ahandle(self, *args, **kwargs):
        response = None
        # 处理请求
        if hasattr(self, 'handle_request'):
            if coroutine_function.is_coroutine_function(self.handle_request):
                response = await self.handle_request()
            else:
                response = await asgiref.sync.sync_to_async(self.handle_request, thread_sensitive=True)()
        # 交给对应的函数处理
        if not response:
            response = await self.next(*args, **kwargs)

        # 处理response
        if hasattr(self, 'handle_response'):
            if coroutine_function.is_coroutine_function(self.handle_response):
                response = await self.handle_response(response)
            else:
                response = await asgiref.sync.sync_to_async(self.handle_response, thread_sensitive=True)(response)

        return response

    def __call__(self, *args, **kwargs):
        handler = self.ahandle if coroutine_function.is_coroutine_function(self) else self.handle
        return handler(*args, **kwargs)
