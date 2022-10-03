import re
import json
from typing import Union

from Vank.core.http import http_status_dict


class BaseResponse:
    def __init__(self,
                 data,
                 status=200,
                 header=None,
                 *args,
                 **kwargs):

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

    @property
    def status(self):
        return f"{self.status_code} {http_status_dict.get(self.status_code, 'Unknow Code')}"


class Response404(BaseResponse):
    def __init__(self, error: Union[dict, str], *args, **kwargs):
        """
        资源未找到
        :param error:
        :param args:
        :param kwargs:
        """
        super(Response404, self).__init__(data=error, status=404,*args, **kwargs)


class Response405(BaseResponse):
    def __init__(self, error: Union[dict, str], *args, **kwargs):
        """
        方法不允许
        :param error:错误数据
        :param args:
        :param kwargs:
        """
        super(Response405, self).__init__(data=error, status=405,*args, **kwargs)


class Response(BaseResponse):
    def __init__(self, data: Union[str, dict, bytes],
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
        super(Response, self).__init__(data, header=headers, *args, **kwargs)


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


class ResponseRedirect(BaseResponse):
    def __init__(self,
                 *args,
                 **kwargs):
        status = 301
        super(ResponseRedirect, self).__init__(None, )
