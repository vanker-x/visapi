import typing as t
from functools import cached_property

from visapi.interface._types import WebsocketScheme


class Websocket:
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send

    @property
    def path(self) -> str:
        return self.scope["path"]

    @cached_property
    def query(self):
        return {}

    @property
    def scheme(self) -> WebsocketScheme:
        return self.scope["scheme"]
