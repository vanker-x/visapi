import os
import json
import aiofiles
import typing as t
from urllib.parse import quote
from mimetypes import guess_type
from vank.core.config import conf
from email.utils import formatdate
from http.cookies import SimpleCookie
from vank.core.http import http_status_dict
from vank.utils.datastructures import Headers
from asgiref.sync import async_to_sync, sync_to_async


class _StopIteration(Exception):
    pass


Content = t.Union[bytes, str]
StreamContent = t.Union[t.AsyncIterable[Content], t.Iterable[Content]]


class Response:
    status: int = 200
    media_type: str = "text/plain"
    charset: str = conf.DEFAULT_CHARSET

    def __init__(
            self,
            content: t.Optional[Content] = None,
            media_type: t.Optional[str] = None,
            status: t.Optional[int] = None,
            headers: t.Optional[t.Dict[str, str]] = None
    ):
        self.status = status or self.status
        self.media_type = media_type or self.media_type
        self.content = content or b""
        self.raw_headers = headers

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: Content):
        self._content = self.str_to_bytes(value)

    @property
    def status_code(self) -> str:
        return f"{self.status} {http_status_dict.get(self.status, 'Unknown Status Code')}"

    @property
    def headers(self) -> Headers:
        if not hasattr(self, '_headers'):
            if not self.raw_headers:
                self._headers = Headers()
            else:
                self._headers = Headers(self.raw_headers.items())
            # 设置Content-Type
            if 'Content-Type' not in self._headers:
                content_type = self.media_type
                if self.media_type.startswith('text/') and 'charset' not in self.media_type:
                    content_type = f'{self.media_type}; charset={self.charset}'
                self._headers.add('Content-Type', content_type)
            # 设置content-length
            if 'Content-Length' not in self._headers:
                if self.content and self.status >= 200 and self.status not in (204, 304):
                    self._headers.setdefault('Content-Length', str(len(self.content)))
        return self._headers

    def add_cookie(
            self,
            key: str,
            value: t.Optional[str] = "",
            max_age: t.Optional[t.Union[int, str]] = None,
            expires: t.Optional[t.Union[int, str]] = None,
            path: t.Optional[str] = "/",
            domain: t.Optional[str] = None,
            secure: t.Optional[bool] = False,
            httponly: t.Optional[bool] = False,
            same_site: t.Optional[str] = None
    ):
        # 当max_age 和expires同时提供时 绝大多数浏览器除了IE会将expires忽略
        # 换而言之就是expires会失效
        self.cookies[key] = value
        cookie = self.cookies[key]
        if max_age:
            cookie['max-age'] = max_age
        if expires:
            cookie['expires'] = expires
        if path:
            cookie['path'] = path
        if domain:
            cookie['domain'] = domain
        if secure:
            cookie['secure'] = True
        if httponly:
            cookie['httponly'] = True
        if same_site:
            assert same_site in ["lax", "none", "strict"], \
                'The value of same_site must be one of "lax", "none", or "strict"'
            cookie['samesite'] = same_site

    def delete_cookie(
            self,
            key: str,
            path: t.Optional[str] = "/",
            domain: t.Optional[str] = None,
            secure: t.Optional[bool] = False,
            httponly: t.Optional[bool] = False,
            same_site: t.Optional[str] = None
    ):
        self.add_cookie(
            key,
            max_age=0,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",  # 设置此值可以将cookie删除
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            same_site=same_site
        )

    @property
    def cookies(self):
        if not hasattr(self, '_cookies'):
            self._cookies = SimpleCookie()
        return self._cookies

    def str_to_bytes(self, content: t.Union[str, bytes]):
        if isinstance(content, bytes):
            return content
        elif isinstance(content, str):
            return content.encode(self.charset)

    def __iter__(self):
        yield self.content

    async def __aiter__(self):
        yield self.content


class JsonResponse(Response):
    media_type = "application/json"

    def __init__(
            self,
            obj: t.Any,
            json_kwargs: t.Optional[t.Dict[str, str]] = None,
            *args,
            **kwargs
    ):
        content = json.dumps(
            obj,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),  # 获得最紧凑的json
            **(json_kwargs or {})
        )
        super(JsonResponse, self).__init__(content, *args, **kwargs)


class StreamResponse(Response):
    def __init__(self, stream: StreamContent, *args, **kwargs):
        super(StreamResponse, self).__init__(content=None, *args, **kwargs)
        self.stream = stream
        self.headers.remove("Content-Length")

    @property
    def stream(self) -> StreamContent:
        return self._stream

    @stream.setter
    def stream(self, stream: StreamContent):
        if not isinstance(stream, (t.AsyncIterable, t.Iterable)):
            raise ValueError("stream must be an async/sync iterable")
        self._stream = stream

    def __iter__(self):
        if isinstance(self.stream, t.Iterable):
            for chunk in self.stream:
                yield self.str_to_bytes(chunk)
        else:
            async def consume(async_iterable: t.AsyncIterable):
                """
                consume async-iterable object.
                :param async_iterable:
                :return:
                """
                result = []
                async for chunk in async_iterable:
                    result.append(chunk)
                return result

            for chunk in async_to_sync(consume)(self.stream):
                yield self.str_to_bytes(chunk)

    async def __aiter__(self):
        if isinstance(self.stream, t.Iterable):
            iterator = iter(self.stream)

            def call_next(sync_iterator: t.Iterator):
                """
                Calling next in the thread pool to avoid blocking
                :param sync_iterator:
                :return:
                """
                try:
                    return next(sync_iterator)
                except StopIteration:
                    raise _StopIteration

            while 1:
                try:
                    data = await sync_to_async(call_next)(iterator)
                except _StopIteration:
                    break
                else:
                    yield self.str_to_bytes(data)

        else:
            async for chunk in self.stream:
                yield self.str_to_bytes(chunk)


class FileResponse(Response):
    chunk_size = 1024 * 128
    media_type = "application/octet-stream"

    def __init__(
            self,
            filepath: t.Union[str, os.PathLike],
            filename: t.Optional[str] = None,
            as_attachment: bool = False,
            media_type: t.Optional[str] = None,
            status: t.Optional[int] = None,
            headers: t.Optional[t.Dict[str, str]] = None,
            chunk_size: t.Optional[int] = None,
            content_range: t.Optional[t.Tuple[int, int]] = None
    ):
        self.chunk_size = chunk_size or self.chunk_size
        self.filename = filename
        self.filepath = filepath
        self.as_attachment = as_attachment
        self.content_range = content_range
        headers = headers or {}
        if media_type is None:
            media_type, encoding = guess_type(filename or filepath)
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f'"{self.filepath}"file does not exist')
        if not os.path.isfile(self.filepath):
            raise TypeError(f'"{self.filepath}"this is not a file')
        stat = os.stat(self.filepath)
        content_length = stat.st_size
        if content_range:
            if status and not status == 206:
                raise ValueError("status must be 206 when content_range parameter is provided")
            start, end = self.content_range
            if not end > start >= 0:
                raise ValueError("Invalid content range: The ending position must be "
                                 "greater than the starting position, and both must be non-negative integers.")
            headers["Content-Range"] = f"bytes {start}-{end}/{content_length}"
            headers['Content-Length'] = str(end - start + 1)
            status = 206
        else:
            headers['Content-Length'] = str(content_length)
        if self.as_attachment:
            if self.filename:
                if (quoted := quote(self.filename)) == self.filename:
                    content_disposition = f'attachment; filename="{self.filename}"'
                else:
                    content_disposition = f"attachment; filename*=utf-8''{quoted}"
            else:
                content_disposition = "attachment"
        else:
            content_disposition = "inline"
        headers['Last-Modified'] = formatdate(stat.st_mtime, usegmt=True)
        headers['Content-Disposition'] = content_disposition
        super(FileResponse, self).__init__(b"", media_type, status, headers)

    def __iter__(self):
        with open(self.filepath, "rb") as f:
            if self.content_range:
                start, end = self.content_range
                # move the cursor to the start position
                f.seek(start)
                total_send = end - start + 1
                while total_send > 0:
                    chunk_size = min(self.chunk_size, total_send)
                    data = f.read(chunk_size)
                    if not data:
                        yield b""
                        break
                    total_send -= chunk_size
                    yield data
            else:
                while 1:
                    data = f.read(self.chunk_size)
                    if not data:
                        yield b""
                        break
                    yield data

    async def __aiter__(self):
        async with aiofiles.open(self.filepath, "rb") as f:
            if self.content_range:
                start, end = self.content_range
                # move the cursor to the start position
                await f.seek(start)
                total_send = end - start + 1
                while total_send > 0:
                    chunk_size = min(self.chunk_size, total_send)
                    data = await f.read(chunk_size)
                    if not data:
                        yield b""
                        break
                    total_send -= chunk_size
                    yield data
            else:
                while 1:
                    data = await f.read(self.chunk_size)
                    if not data:
                        yield b""
                        break
                    yield data


class BadRequest(Response):
    status = 400


class NotAuthorizedResponse(Response):
    status = 401


class ForbiddenResponse(Response):
    status = 403


class NotFoundResponse(Response):
    status = 404


class MethodNotAllowedResponse(Response):
    status = 405

    def __init__(self, allow: t.Sequence[str], *args, **kwargs):
        """
        Initializes a MethodNotAllowedResponse object.
        :param allow: a sequence of allowed HTTP methods for the requested resource.
        :param args: additional positional arguments passed to the parent class Response.
        :param kwargs: additional keyword arguments passed to the parent class Response.
        """
        super(MethodNotAllowedResponse, self).__init__(b"", *args, **kwargs)
        self.headers.setdefault('Allow', ','.join(allow))


class InternalServerError(Response):
    status = 500


class HTMLResponse(Response):
    media_type = "text/html"


class RedirectResponse(Response):
    status = 301

    def __init__(
            self,
            url: str,
            permanent: t.Optional[bool] = True,
            media_type: t.Optional[str] = None,
            headers: t.Optional[t.Dict[str, str]] = None
    ):
        """
        Initializes a RedirectResponse object.
        :param url: the URL to which the request is redirected.
        :param permanent: a boolean indicating whether the redirection is permanent (True) or temporary (False).
        """
        # 判断是否永久重定向 301为永久重定向
        super(RedirectResponse, self).__init__(status=301 if permanent else 302, media_type=media_type, headers=headers)
        self.headers.setdefault('Location', quote(url, safe="/#%[]=:;$&()+,!?*@'~"))
