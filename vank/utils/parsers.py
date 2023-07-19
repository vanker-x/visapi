import typing as t
from urllib.parse import parse_qsl
from vank.utils.datastructures import Form, SpooledUploadFile


class ParseException(Exception):
    """
    解析时异常
    """


class MultiPartFormParser:
    """
    multipart-form/data解析器
    规范：
    https://datatracker.ietf.org/doc/html/rfc7578#section-4.1
    """

    def __init__(self, content_parameter, body, charset: t.Optional[str] = 'utf-8'):
        self.boundary = content_parameter[b'boundary']
        self.body = body
        self.charset = charset

    def run(self):
        form = Form()
        parts = self.body.split(b"--" + self.boundary)
        parts = parts[1:-1]
        for part in parts:
            header, content = part.split(b'\r\n\r\n', 1)
            content = content.strip(b'\r\n')
            headers = dict([line.split(b': ', 1) for line in header.split(b'\r\n')[1:]])
            ctype, rest = headers.get(b'Content-Disposition').split(b'; ', 1)
            mapped_content_disposition = dict(line.split(b'=') for line in rest.split(b'; '))
            mapped_content_disposition = dict(
                (key, value.strip(b'"')) for key, value in mapped_content_disposition.items())
            try:
                field_name = mapped_content_disposition[b"name"]
            except KeyError:
                raise ParseException("Content-Disposition标头字段'name'必须提供")
            else:
                field_name = field_name.decode(self.charset)
            # 如果filename在content_dispositions中,那么该部分为文件
            if b"filename" in mapped_content_disposition.keys():
                filename = mapped_content_disposition[b'filename'].decode(self.charset)
                content_type = headers.get(b'Content-Type', b"").decode(self.charset)
                field_value = SpooledUploadFile(filename, content_type, mapped_content_disposition)
                field_value.write(content)
                field_value.seek(0)
            else:
                field_value = content.decode(self.charset)
            form.append_value(field_name, field_value, error=False)
        return form


class FormParser:
    def __init__(self, stream):
        self.stream = stream

    def run(self):
        form = Form()
        for key, value in parse_qsl(self.stream.decode("latin1"), keep_blank_values=False):
            form.append_value(key, value, error=False)
        return form
