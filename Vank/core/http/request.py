import json
from http import cookies
from urllib.parse import unquote_plus, parse_qsl
from Vank.core.config import conf
from Vank.utils.parsers import MultiPartParser, FormParser
from Vank.utils.datastructures import Form
from multipart.multipart import parse_options_header


class RequestMeta:
    def __init__(self, environ: dict):
        for k, v in environ.items():
            setattr(self, k, v)


class BaseRequest:
    def __init__(self, environ: dict):
        self.environ = environ
        # 设置元信息
        self.meta = RequestMeta(environ)
        self._json = None
        self._form = None
        self._content_type = None
        self._content_params = None
        self._path = None
        self._stream = None
        self._method = None

    @property
    def path(self):
        """
        获取请求路径
        :return:
        """
        if getattr(self, '_path') is None:
            path_info = self.environ.get('PATH_INFO', '/').encode('latin-1').decode()
            self._path = unquote_plus(path_info, self.charset, 'replace')
        return self._path

    @property
    def content_params(self):
        """
        获取content-type后的options
        :return:
        """
        if getattr(self, '_content_params') is None:
            self._content_params = parse_options_header(self.environ.get('CONTENT_TYPE', ''))[1]

        return self._content_params

    @property
    def content_type(self):
        """
        获取content-type
        :return:
        """
        if getattr(self, '_content_type') is None:
            self._content_type = parse_options_header(self.environ.get('CONTENT_TYPE', ''))[0].decode()
        return self._content_type

    @property
    def stream(self):
        """
        获取数据二进制流
        :return:
        """
        if getattr(self, '_stream') is None:
            self._stream = self.environ.get('wsgi.input').read(self.content_length)
        return self._stream

    @property
    def json(self):
        """
        解析body
        :return:
        """
        _dic = {}
        if getattr(self, '_json') is None:

            if self.content_type.lower() == 'application/json':
                _dic.update(json.loads(self.stream))
            setattr(self, '_json', _dic)
        return _dic

    @property
    def form(self):
        """
        表单
        :return:
        """
        if getattr(self, '_form') is None:
            if self.content_type == 'multipart/form-data':
                parser = MultiPartParser(self.content_type, self.content_params, self.stream, self.charset)
                setattr(self, '_form', parser.run())
            elif self.content_type == 'application/x-www-form-urlencoded':
                parser = FormParser(self.stream)
                setattr(self, '_form', parser.run())
            else:
                setattr(self, '_form', Form())
        return self._form

    @property
    def charset(self):
        """
        获取charset
        :return:
        """
        if not hasattr(self, '_charset'):
            setattr(self, '_charset', self.content_params.get('charset', 'utf-8'))
        return self._charset

    @property
    def content_length(self):
        """
        获取到content-length
        :return:
        """
        if not hasattr(self, '_content_length'):
            content_length = self.environ.get('CONTENT_LENGTH', 0)
            try:
                content_length = int(content_length)
            except Exception as e:
                content_length = 0
            setattr(self, '_content_length', content_length)
        return self._content_length

    @property
    def method(self):
        """
        获取请求方法
        :return:
        """
        if getattr(self, '_method') is None:
            method = self.environ.get('REQUEST_METHOD').upper()
            setattr(self, '_method', method)

        return self._method

    @property
    def param(self):
        """
        获取URL查询参数
        :return:
        """

        if not hasattr(self, '_param'):
            qs = self.environ.get('QUERY_STRING', '').encode('latin-1').decode('utf-8')
            qs = parse_qsl(qs, keep_blank_values=True)

            setattr(self, '_param', {k: v for k, v in qs})

        return self._param

    @property
    def cookies(self):
        """
        获取cookie
        :return:
        """
        cookie_dict = {}
        for cookie in self.environ.get('HTTP_COOKIE', '').split(";"):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
            else:
                key, value = "", cookie
            # 如果key或者value存在 那么就添加到cookie_dict当中
            if key or value:
                cookie_dict[key.strip()] = cookies._unquote(value.strip())

        return cookie_dict

    def close(self):
        if getattr(self, '_form', None) is not None:
            self._form.close()


class Request(BaseRequest):
    def __init__(self, environ: dict):
        super(Request, self).__init__(environ)
