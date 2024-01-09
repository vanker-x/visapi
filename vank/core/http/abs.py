import typing as t
from vank.core import conf
from vank.types import HTTPMethod
from email.message import Message
from abc import ABC, abstractmethod
from functools import cached_property
from http.cookies import SimpleCookie
from vank.utils.datastructures import QueryString, Headers, Form


class RequestLine(ABC):
    @property
    @abstractmethod
    def path(self) -> str:
        ...

    @property
    @abstractmethod
    def method(self) -> HTTPMethod:
        ...

    @property
    @abstractmethod
    def query(self) -> QueryString:
        ...


class RequestHeader(ABC):
    def _setup_content_type(self):
        """
        Parse content-type header
        :return: nothing
        """
        message = Message()
        message['content-type'] = self.headers.get('CONTENT_TYPE')
        params = message.get_params()
        self._content_type = params[0][0]
        self._content_params = dict(params[1:])

    @property
    def content_params(self) -> dict:
        """
        Content params for current HTTP request
        :return: content-params
        """
        if not hasattr(self, "_content_params"):
            self._setup_content_type()
        return self._content_params

    @property
    def content_type(self) -> str:
        """
        Content type for current HTTP request
        :return: content-type
        """
        if not hasattr(self, "_content_type"):
            self._setup_content_type()
        return self._content_type

    @cached_property
    def charset(self) -> str:
        """
        Charset for current HTTP request and default is DEFAULT_CHARSET from user configration
        :return: charset
        """
        return self.content_params.get("charset", conf.DEFAULT_CHARSET)

    @cached_property
    def content_length(self) -> int:
        """
        Content length for current HTTP request and default is 0
        if CONTENT_LENGTH not in request headers
        :return: content length
        """
        try:
            content_length = int(self.headers.get("CONTENT_LENGTH", 0))
        except Exception as e:
            content_length = 0
        return content_length

    @cached_property
    def cookies(self) -> SimpleCookie:
        """
        The cookies for the current HTTP request
        :return: SimpleCookie object
        """
        return SimpleCookie(self.headers.get('COOKIE', ''))

    @property
    @abstractmethod
    def headers(self) -> Headers:
        ...


class RequestBody(ABC):

    @property
    @abstractmethod
    def json(self, raise_error=False) -> t.Any:
        ...

    @property
    @abstractmethod
    def form(self) -> Form:
        ...

    def close(self):
        if hasattr(self, "_form"):
            self.form.close()
