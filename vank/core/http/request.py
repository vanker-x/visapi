import json
import typing as t
from cgi import parse_header
from http.cookies import SimpleCookie
from urllib.parse import unquote_plus, parse_qsl
from vank.utils.parsers import FormParser, MultiPartFormParser
from vank.utils.datastructures import Form, Headers, QueryString


class BaseRequest:
    def __init__(self, environ: dict):
        self.environ: dict = environ
        self._json: t.Union[None, t.Dict[str, t.Any]] = None
        self._form: t.Union[None, Form] = None
        self._content_type: t.Union[None, str] = None
        self._content_params: t.Union[None, dict] = None
        self._path: t.Union[None, str] = None
        self._stream: t.Union[None, bytes] = None
        self._method: t.Union[None, str] = None
        self._headers: t.Union[None, Headers] = None
        self._cookies: t.Union[None, SimpleCookie] = None
        self._query: t.Union[None, QueryString] = None

    @property
    def headers(self) -> Headers:
        if getattr(self, '_headers') is None:
            self._headers = Headers(parse_headers(environ=self.environ))
        return self._headers

    @property
    def path(self) -> str:
        """
        获取请求路径
        :return:
        """
        if self._path is None:
            path_info = self.environ.get('PATH_INFO', '/').encode('latin-1').decode()
            self._path = unquote_plus(path_info, self.charset, 'replace')
        return self._path

    def _set_up_content_type(self):
        self._content_type, self._content_params = parse_header(self.headers.get('CONTENT_TYPE', ''))

    @property
    def content_params(self) -> dict:
        """
        获取content-type后的options
        :return:
        """
        if self._content_params is None:
            self._set_up_content_type()
        return self._content_params

    @property
    def content_type(self) -> str:
        """
        获取content-type
        :return:
        """
        if self._content_type is None:
            self._set_up_content_type()
        return self._content_type

    @property
    def stream(self) -> bytes:
        """
        读取字节流
        :return:
        """
        if self._stream is None:
            self._stream = self.environ.get('wsgi.input').read(self.content_length)
        return self._stream

    @property
    def json(self) -> t.Any:
        """
        解析body
        :return:
        """
        if self._json is None:
            if self.content_type.lower() == 'application/json':
                self._json = json.loads(self.stream) or None
        return self._json

    @property
    def form(self) -> Form:
        """
        表单
        :return:
        """
        if self._form is None:
            if self.content_type == 'multipart/form-data':
                parser = MultiPartFormParser(self.content_params, self.stream, self.charset)
                form = parser.run()
            elif self.content_type == 'application/x-www-form-urlencoded':
                parser = FormParser(self.stream)
                form = parser.run()
            else:
                form = Form()
            self._form = form
        return self._form

    @property
    def charset(self) -> str:
        """
        获取charset
        :return:
        """
        if not hasattr(self, '_charset'):
            setattr(self, '_charset', self.content_params.get('charset', 'utf-8'))
        return self._charset

    @property
    def content_length(self) -> int:
        """
        获取到content-length
        :return:
        """
        if not hasattr(self, '_content_length'):
            content_length = self.headers.get('CONTENT_LENGTH', 0)
            try:
                content_length = int(content_length)
            except Exception as e:  # noqa
                content_length = 0
            setattr(self, '_content_length', content_length)
        return self._content_length  # noqa

    @property
    def method(self) -> str:
        """
        获取请求方法
        :return:
        """
        if self._method is None:
            self._method = self.environ.get('REQUEST_METHOD').upper()

        return self._method

    @property
    def query(self) -> QueryString:
        """
        获取URL查询参数
        :return:
        """
        if self._query is None:
            self._query = QueryString()
            qs = self.environ.get('QUERY_STRING', '').encode('latin-1').decode('utf-8')
            for key, value in parse_qsl(qs, keep_blank_values=True):
                self.query.append_value(key, value, error=False)

        return self._query  # noqa

    @property
    def cookies(self) -> dict:
        """
        获取cookie
        :return:
        """
        if self._cookies is None:
            self._cookies = SimpleCookie(self.headers.get('COOKIE', ''))
        return self._cookies

    def close(self):
        if getattr(self, '_form', None) is not None:
            self._form.close()

    def remote_address(self, pre_proxy_number=1) -> str:
        """
        你可以通过设置pre_proxy_number（反向代理服务器数量）获取客户端的ip地址；
        详情见：https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/X-Forwarded-For
        下面是获取客户端ip地址的取值优先级
        1.x-forwarded-for  此项需要由反向代理服务器设置(当存在多个反向代理服务器时，x-forwarded-for减去反向代理服务器数量的最后一个为客户端ip地址)
        2.remote-addr      此项需要由反向代理服务器设置(当只有一个反向代理服务器时，此项为与其连接的客户端的ip地址)
        3.environ中的remote-addr 此项为与WSGI服务器连接的客户端的ip地址

        :param pre_proxy_number:代理服务器数量
        :return:
        """
        try:
            x_forwarded_for_list = self.headers.get('X_FORWARDED_FOR', '').split(',')
            x_forwarded_for = [item.strip() for item in x_forwarded_for_list if item.strip()]
            if pre_proxy_number == 0:
                return x_forwarded_for[-1]
            real_address_index = len(x_forwarded_for) - pre_proxy_number
            if real_address_index < 1:
                raise IndexError
            return x_forwarded_for[real_address_index - 1]
        except (IndexError, AttributeError):
            return self.headers.get('X_REMOTE_ADDR', None) or self.environ.get('REMOTE_ADDR', None)


class Request(BaseRequest):
    def __init__(self, environ: dict):
        super(Request, self).__init__(environ)


def parse_headers(environ: dict) -> tuple:
    """
    解析HTTP头
    :param environ: WSGI environ
    :return: dict
    """
    for header_name, header_value in environ.items():
        # 判断是否以HTTP_开头
        if header_name.startswith('HTTP_'):
            header = (header_name.split('HTTP_', 1)[-1], header_value)
        elif header_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            header = (header_name, header_value)
        else:
            continue
        yield header
