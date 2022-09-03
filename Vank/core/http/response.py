import json
import re

from .status import *
from typing import Union


class BasicResponse:
    def __init__(self, request, data, status=HTTP_200_OK, header=None, *args, **kwargs):

        self.status_code = status
        encoder = json.JSONEncoder(ensure_ascii=False)
        if isinstance(data, dict):
            self.data = encoder.encode(data).encode()

        if isinstance(data, str):
            self.data = data.encode()

        if isinstance(data, bytes):
            self.data = data
        if not header:
            self.header = {'Content-Type': 'application/json'}
        else:
            self.header = header

    def charset(self):
        pattern = re.compile(r';\s*charset=(?P<charset>[^\s;]+)', re.I)
        mached = pattern.search(self.header.get('Content-Type', ''))
        if not mached:
            return 'utf-8'


class Response404(BasicResponse):
    def __init__(self, request, error: Union[dict, str], *args, **kwargs):
        '''
        资源未找到
        :param error:
        :param args:
        :param kwargs:
        '''
        super(Response404, self).__init__(request, data=error, status=HTTP_404_NOT_FOUND)


class Response405(BasicResponse):
    def __init__(self, request, error: Union[dict, str], *args, **kwargs):
        '''
        方法不允许
        :param error:错误数据
        :param args:
        :param kwargs:
        '''
        super(Response405, self).__init__(request, data=error, status=HTTP_405_METHOD_NOT_ALLOWED)


class Response(BasicResponse):
    def __init__(self, request, data: Union[str, dict, bytes], status: int = HTTP_200_OK, headers={}, *args,
                 **kwargs):
        '''
        普通响应
        :param data:响应数据
        :param status:状态码
        :param headers:响应头
        :param args:
        :param kwargs:
        '''
        super(Response, self).__init__(request, data, status, headers, *args, **kwargs)


class ResponseStreaming(BasicResponse):
    def __init__(self, request, stream: bytes, status, *args, **kwargs):
        '''
        流响应
        :param stream:二进制数据
        :param status:状态码
        :param args:
        :param kwargs:
        '''
        super(ResponseStreaming, self).__init__(request, stream, status, *args, **kwargs)
