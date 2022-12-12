import cgi
import json
from http import cookies
from urllib.parse import unquote_plus
from functools import cached_property

from Vank.core.config import conf
from Vank.utils.parsers import MultiPartParser

class RequestMeta:
    def __init__(self, environ: dict):
        for k, v in environ.items():
            setattr(self, k, v)


class BaseRequest:
    def __init__(self, environ: dict):
        self.environ = environ
        # 设置元信息
        self.meta = RequestMeta(environ)

    @cached_property
    def path(self):
        """
        获取请求路径
        :return:
        """
        path_info = self.environ.get('PATH_INFO', '/')
        return unquote_plus(path_info, self.charset, 'replace')

    @cached_property
    def content_params(self):
        """
        获取content-type后的options
        :return:
        """
        return cgi.parse_header(self.environ.get('CONTENT_TYPE', ''))[1]

    @cached_property
    def content_type(self):
        """
        获取content-type
        :return:
        """
        return cgi.parse_header(self.environ.get('CONTENT_TYPE', ''))[0]

    @cached_property
    def stream(self):
        """
        获取数据二进制流
        :return:
        """
        return self.environ.get('wsgi.input').read(self.content_length)

    @cached_property
    def json(self):
        """
        解析body
        :return:
        """
        # TODO 完善数据获取
        data_dic = {}
        if self.content_type.lower() == 'application/json':
            data_dic.update(json.loads(self.stream))

        return data_dic

    @cached_property
    def files(self):
        """
        获取文件
        :return:
        """
        # TODO 完善文件解析
        if not self.method == 'POST':
            return {}

        content_type = self.content_type

        if content_type == 'multipart/form-data':
            parser = MultiPartParser(self.content_type, self.content_params, self.stream)
            parser.run()
            return

        elif content_type == 'application/x-www-form-urlencoded':
            return

        return {}

    @cached_property
    def charset(self):
        """
        获取charset
        :return:
        """
        return self.content_params.get('charset', 'utf-8')

    @cached_property
    def content_length(self):
        """
        获取到content-length
        :return:
        """
        content_length = self.environ.get('CONTENT_LENGTH', 0)
        try:
            return int(content_length)
        except:
            return 0

    @cached_property
    def method(self):
        """
        获取请求方法
        :return:
        """
        return self.environ.get('REQUEST_METHOD').upper()

    @cached_property
    def param(self):
        """
        获取URL查询参数
        :return:
        """
        query_string = self.environ.get('QUERY_STRING', '').encode('latin1')
        query_dict = {}
        for item in query_string.decode(self.charset).split('&'):
            if '=' in item:
                key, value = item.split('=')
                query_dict.update({unquote_plus(key): unquote_plus(value)})
        return query_dict

    @cached_property
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


class Request(BaseRequest):
    def __init__(self, environ: dict):
        super(Request, self).__init__(environ)
