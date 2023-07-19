import os
import re
import json
import typing as t
from urllib.parse import quote
from mimetypes import guess_type
from vank.core.config import conf
from email.utils import formatdate
from http.cookies import SimpleCookie
from vank.core.http import http_status_dict
from vank.utils.datastructures import Headers


class BaseResponse:
    default_status = 200
    media_type = 'text/plain'

    def __init__(self,
                 content: t.Optional[t.Union[bytes, str]] = b"",
                 status: t.Optional[int] = None,
                 headers: t.Optional[t.Union[dict, Headers]] = None,
                 media_type: str = None,
                 ):
        # 判断status是否传入  如果没有传入那么就设置未默认的status
        self._status = status or self.default_status
        self._charset = None
        self._content = content or b""
        self._body = None
        self._raw_headers = headers
        self._headers = None
        self._cookies = None
        self.media_type = media_type or self.media_type

    @property
    def body(self):
        if getattr(self, '_body') is None:
            if isinstance(self._content, bytes):
                self._body = self._content
            else:
                self._body = self._content.encode(self.charset)
        return self._body

    @property
    def headers(self):
        if getattr(self, '_headers') is None:
            if not self._raw_headers:
                self._headers = Headers()
            elif isinstance(self._raw_headers, Headers):
                self._headers = self._raw_headers
            else:
                self._headers = Headers(self._raw_headers)
            # 设置Content-Type
            if 'Content-Type' not in self._headers:
                content_type = self.media_type
                if content_type.startswith('text/') and 'charset' not in content_type:
                    content_type = f'{content_type}; charset={self.charset}'
                self._headers.add('Content-Type', content_type)
            # 设置content-length
            if 'Content-Length' not in self._headers:
                if self.body and self._status >= 200 and self._status not in (204, 304):
                    self._headers.setdefault('Content-Length', str(len(self.body)))
        return self._headers

    @property
    def charset(self):
        if getattr(self, '_charset') is None:
            pattern = re.compile(r';\s*charset=(?P<charset>[^\s;]+)', re.I)
            res = pattern.search(self.headers.get('Content-Type', ''))
            if not res:
                self._charset = conf.DEFAULT_CHARSET
            else:
                self._charset = res.groupdict().get('charset')
        return self._charset

    @property
    def status(self):
        return f"{self._status} {http_status_dict.get(self._status, 'Unknow Status Code')}"

    def __iter__(self):
        yield from [self.body]

    def add_cookie(self,
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
            assert same_site in ["lax", "none", "strict"], 'same_site的值必须为 "lax", "none", "strict"'
            cookie['samesite'] = same_site

    def delete_cookie(self,
                      key: str,
                      path: t.Optional[str] = "/",
                      domain: t.Optional[str] = None,
                      secure: t.Optional[bool] = False,
                      httponly: t.Optional[bool] = False,
                      same_site: t.Optional[str] = None):
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
        if getattr(self, '_cookies') is None:
            self._cookies = SimpleCookie()
        return self._cookies


class ResponsePlain(BaseResponse):
    def __init__(self,
                 content: t.Optional[t.Union[bytes, str]] = b"",
                 status=200,
                 headers=None,
                 *args,
                 **kwargs):
        """
        普通响应
        :param data:响应数据
        :param status:状态码
        :param headers:响应头
        :param args:
        :param kwargs:
        """
        super(ResponsePlain, self).__init__(content, status, headers=headers, *args, **kwargs)


class Response404(BaseResponse):
    """
    资源未找到 404
    """
    default_status = 404


class Response403(BaseResponse):
    """
    403 Forbidden
    """
    default_status = 403


class Response400(BaseResponse):
    """
    Bad request 400
    """
    default_status = 400


class Response500(BaseResponse):
    """
    server 500 响应
    """
    default_status = 500


class Response405(BaseResponse):
    """
    Method not allowed 响应
    """
    default_status = 405

    def __init__(self, allow, *args, **kwargs):
        """
        方法不允许
        :param error:错误数据
        :param args:
        :param kwargs:
        """
        super(Response405, self).__init__(b"", *args, **kwargs)
        self.headers.setdefault('Allow', ','.join(allow))


class ResponseStreaming(BaseResponse):
    def __init__(self, stream: bytes,
                 *args,
                 **kwargs):
        """
        流响应
        :param stream:二进制数据
        :param args:
        :param kwargs:
        """
        super(ResponseStreaming, self).__init__(stream, *args, **kwargs)


class ResponseFile(BaseResponse):
    """
    将文件根据chunk_size以块的方式读入到内存当中,
    """
    chunk_size = 2048
    media_type = 'application/octet-stream'

    def __init__(self, filepath: str, filename=None, as_attachment=True, media_type=None, *args, **kwargs):
        assert not kwargs.get('content', None), 'ResponseFile不应该有content'
        self.as_attachment = as_attachment
        self.filepath = os.path.abspath(filepath)
        self.filename = filename
        self.user_media_type = media_type
        super(ResponseFile, self).__init__(*args, **kwargs)
        self.update_headers()

    def update_headers(self):
        # 判断文件是否存在 如果不存在那么raise FileNotFoundError
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f'{self.filepath}文件不存在')
        if not os.path.isfile(self.filepath):
            raise TypeError(f'{self.filepath}不是文件')
        # 获取文件的统计信息
        stat = os.stat(self.filepath)
        # 根据统计信息的st_size 可以获取到文件的长度
        content_length = stat.st_size
        # 获取最后修改时间
        last_modified = formatdate(stat.st_mtime, usegmt=True)
        if self.filename:
            # attachment 和 inline 可以控制浏览器的行为 attachment 是作为附件下载 而 inline 是作为普通网页取浏览
            disposition_type = 'attachment' if self.as_attachment else 'inline'
            # 这里需要解决非ascii编码的问题以符合URL规范
            if quote(self.filename) == self.filename:
                content_disposition = f'{disposition_type}; filename="{self.filename}"'
            else:
                content_disposition = f"{disposition_type}; filename*=utf-8''{quote(self.filename)}"
        else:
            content_disposition = 'attachment'
        # 判断是否提供media_type 如果没有提供
        # 那么根据filename 或者filepath 的后缀 guess_type 获取media_type
        # 当guess_type 返回值为None时 则默认为 application/octet-stream
        if self.user_media_type is None:
            content_type, encoding = guess_type(self.filename or self.filepath)
        else:
            content_type = self.user_media_type
        self.headers.update('Content-Length', str(content_length))
        self.headers.update('Last-Modified', last_modified)
        self.headers.update('Content-Disposition', content_disposition)
        if content_type:  # guess_type 时 content_type 可能为None
            self.headers.update('Content-Type', content_type)

    def __iter__(self):
        with open(self.filepath, 'rb') as f:
            while 1:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    yield b""
                    break
                yield chunk


class ResponseRedirect(BaseResponse):
    default_status = 301

    def __init__(self, url, permanent=True, *args, **kwargs):
        # 判断是否永久重定向 301为永久重定向
        if not permanent:
            self.default_status = 302
        super(ResponseRedirect, self).__init__(*args, **kwargs)

        self.headers.update('Location', quote(url, safe="/#%[]=:;$&()+,!?*@'~"))


class ResponseJson(BaseResponse):
    media_type = f'application/json'

    def __init__(self, content: t.Any, *args, **kwargs):
        content = json.dumps(
            content,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),  # 获得最紧凑的json
        )

        super(ResponseJson, self).__init__(content, *args, **kwargs)


class ResponseHtml(BaseResponse):
    media_type = "text/html"
