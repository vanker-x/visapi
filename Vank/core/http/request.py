import json
import wsgiref.util
from typing import Dict
from urllib.parse import quote
from Vank.core import exceptions
import cgi


class RequestMeta:
    def __init__(self, environ: dict):
        for k, v in environ.items():
            setattr(self, k, v)


class BasicRequest:
    def __init__(self, environ: dict):
        self.environ = environ
        # 设置元信息
        self.meta = RequestMeta(environ)
        # 请求路径
        self.path: str = quote(environ.get('PATH_INFO'))

        # 解析后的查询字典
        self.param: dict = self.__parse_param(environ.get('QUERY_STRING', '').encode('latin1'))

        # 内容类型
        self.content_type, self.content_params = cgi.parse_header(environ.get('CONTENT_TYPE', ''))

        # 读取body中的数据
        self.stream: bytes = environ.get('wsgi.input').read(self.content_length)
        # 解析数据
        self.data: dict = self.__parse_data(self.stream)
        self.file: Dict[str, bytes] = self.__parse_file()

    def __parse_content_length(self, content_length):
        '''
        解析content_length
        '''
        try:
            return int(content_length)
        except ValueError as e:
            return 0

    def __parse_data(self, data: bytes) -> dict:
        data_dic = {}
        '''
        解析body
        '''
        if self.content_type.lower() == 'application/json':
            try:
                data_dic.update(json.loads(data))
            except Exception as e:
                raise

        if self.content_type.lower() == 'multipart/form-data':
            print(data.decode().split('--' + self.content_params.get('boundary')))

        return data_dic

    def __parse_param(self, query) -> dict:
        print(query)
        '''
        解析查询参数
        '''
        query_dic = {}
        for item in query.split('&'):
            if '=' in item:
                key, value = item.split('=')
                query_dic.update({key: value})

        return query_dic

    def __parse_file(self) -> Dict[str, bytes]:
        return {}

    @property
    def charset(self):
        return 'utf-8'

    @property
    def content_length(self):
        content_length = self.environ.get('CONTENT_LENGTH', 0)
        return int(content_length)

    @property
    def method(self):
        return self.environ.get('REQUEST_METHOD')

    @property
    def url_param(self):
        pass

    def __repr__(self):
        return str(self.__dict__)


class Request(BasicRequest):
    def __init__(self, environ: dict):
        super(Request, self).__init__(environ)
