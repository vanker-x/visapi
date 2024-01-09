import json
import typing as t
from vank.types import HTTPMethod
from functools import cached_property
from urllib.parse import unquote_plus, parse_qsl
from vank.utils.parsers import FormParser, MultiPartFormParser
from vank.utils.datastructures import Form, Headers, QueryString
from vank.core.http.abs import RequestLine, RequestBody, RequestHeader


class WSGIRequest(RequestLine, RequestHeader, RequestBody):
    def __init__(self, environ: dict):
        self.environ = environ

    @cached_property
    def headers(self) -> Headers:
        raw = []
        for key, val in self.environ.items():
            if key.startswith("HTTP_") or key.upper() in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                raw.append((key.split("HTTP_", 1)[-1], val))
        return Headers(raw)

    @cached_property
    def method(self) -> HTTPMethod:
        return self.environ.get('REQUEST_METHOD', "").upper()

    @cached_property
    def path(self) -> str:
        path_info = self.environ.get('PATH_INFO', '/').encode('latin-1').decode()
        return unquote_plus(path_info, self.charset, 'replace')

    @property
    def body(self):
        if not hasattr(self, "_body"):
            self._body: bytes = self.environ.get('wsgi.input').read(self.content_length)
        return self._body

    def json(self, raise_error=False) -> t.Any:
        if not hasattr(self, "_json"):
            try:
                self._json = json.loads(self.body)
            except Exception as e:
                if raise_error: raise e
                self._json = None

        return self._json

    @property
    def form(self) -> Form:
        if not hasattr(self, "_form"):
            if self.content_type == 'multipart/form-data':
                parser = MultiPartFormParser(self.content_params.get("boundary"), self.body, )
                form = parser.run()
            elif self.content_type == 'application/x-www-form-urlencoded':
                parser = FormParser(self.body)
                form = parser.run()
            else:
                form = Form()
            self._form = form
        return self._form

    @property
    def query(self) -> QueryString:
        if not hasattr(self, "_query"):
            self._query = QueryString()
            qs = self.environ.get('QUERY_STRING', '').encode('latin-1').decode('utf-8')
            for key, value in parse_qsl(qs, keep_blank_values=True):
                self.query.append_value(key, value, error=False)
        return self._query


class ASGIHeader(RequestHeader):
    """
    Common HTTP header class for ASGIRequest and Websocket
    """

    def __init__(self, scope, receive):
        """
        Initialize
        :param scope: asgi scope
        :param receive: asgi receive
        """
        self._scope = scope
        self._receive = receive

    @cached_property
    def headers(self) -> Headers:
        """
        Generate headers for current HTTP request
        :return: Headers object
        """
        return Headers([
            (
                header_name.decode("latin-1").upper().replace("-", "_"),
                header_val.decode("latin-1")
            )
            for header_name, header_val in self._scope.get("headers", [])])


class ASGIRequest(RequestLine, ASGIHeader, RequestBody):
    @cached_property
    def path(self) -> str:
        """
        Request path
        :return:
        """
        return self._scope.get("path")

    @property
    async def body(self):
        if not hasattr(self, "_body"):
            self._body = b""
            while 1:
                msg = await self._receive()
                if msg.get("type") == "http.disconnect":
                    raise RuntimeError("The HTTP connection has been disconnected")
                self._body += msg.get("body", b"")
                if not msg.get("more_body", False):
                    break
        return self._body

    async def json(self, raise_error=False) -> t.Any:
        if not hasattr(self, "_json"):
            body = await self.body
            try:
                self._json = json.loads(body)
            except Exception as e:
                if raise_error: raise e
                self._json = None

        return self._json

    @property
    async def form(self) -> Form:
        if not hasattr(self, "_form"):
            body = await self.body
            if self.content_type == 'multipart/form-data':
                parser = MultiPartFormParser(self.content_params.get("boundary"), body, )
                form = parser.run()
            elif self.content_type == 'application/x-www-form-urlencoded':
                parser = FormParser(body)
                form = parser.run()
            else:
                form = Form()
            self._form = form
        return self._form

    @cached_property
    def method(self) -> HTTPMethod:
        """
        The method for the current HTTP request
        :return: uppercase http method
        """
        return self._scope.get("method", "").upper()

    @property
    def query(self) -> QueryString:
        """
        The query parameters for the current HTTP request
        :return: QueryString object
        """
        if not hasattr(self, "_query"):
            query = QueryString()
            qs = self._scope.get("query_string", b"").decode('latin-1')
            for key, value in parse_qsl(qs, keep_blank_values=True):
                query.append_value(key, value, error=False)
            self._query = query
        return self._query
