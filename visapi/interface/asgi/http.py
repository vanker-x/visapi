import typing as t
from email.message import Message
from functools import cached_property

from visapi.helpers.http import MultiPartFormParser
from visapi.interface._types import HTTPMethod, HTTPScheme


async def body_iterator(receive):
    while True:
        message = await receive()
        if message.get("type") == "http.disconnect":
            raise RuntimeError("The HTTP connection has been disconnected")
        yield message.get("body")
        if not message.get("more_body", False):
            break


class Request:
    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send

    @cached_property
    def path(self) -> str:
        return self.scope["path"]

    @cached_property
    def method(self) -> HTTPMethod:
        return self.scope["method"].upper()

    @cached_property
    def query(self):
        return {}

    @cached_property
    def parse_content_type(self):
        message = Message()
        message['content-type'] = self.headers.get('CONTENT-TYPE')
        params = message.get_params()
        return params

    @property
    def content_type(self):
        return self.parse_content_type[0][0]

    @property
    def mimetype_params(self):
        return dict(self.parse_content_type[1:])

    @property
    def headers(self):
        return dict(
            (header.decode("latin-1").upper(), value.decode("latin-1"))
            for header, value in self.scope.get("headers", [])
        )

    @cached_property
    async def form(self):
        form = await MultiPartFormParser(body_iterator(self.receive), self.mimetype_params.get("boundary")).parse()

        return form

    @cached_property
    def json(self):
        pass

    @property
    def http_version(self) -> str:
        return self.scope["http_version"]

    @property
    def scheme(self) -> HTTPScheme:
        return self.scope["scheme"]


class Response:
    pass
