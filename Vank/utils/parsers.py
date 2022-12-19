import enum
import multipart
from urllib.parse import unquote_plus
from Vank.utils.datastructures import Form, SpooledUploadFile


class MultipartState(enum.IntEnum):
    PART_BEGIN = 0
    PART_DATA = 1
    PART_END = 2
    HEADER_BEGIN = 3
    HEADER_FIELD = 4
    HEADER_VALUE = 5
    HEADER_END = 6
    HEADERS_FINISHED = 7
    END = 8


class FormState(enum.IntEnum):
    FIELD_START = 0
    FIELD_NAME = 1
    FIELD_DATA = 3
    FIELD_END = 4
    END = 5


class ParseException(Exception):
    """
    解析时异常
    """


class MultiPartParser:
    def __init__(self, content_type, parameters, stream, charset='utf-8'):
        self.content_type = content_type
        self.parameters = parameters
        self._stream = stream
        self.charset = charset
        self.callbacks = {
            'on_end': self.on_end,
            'on_part_end': self.on_part_end,
            'on_part_data': self.on_part_data,
            'on_part_begin': self.on_part_begin,
            'on_header_end': self.on_header_end,
            'on_header_begin': self.on_header_begin,
            'on_header_field': self.on_header_field,
            'on_header_value': self.on_header_value,
            'on_headers_finished': self.on_headers_finished,
        }
        self.messages = []

    def on_part_begin(self):
        self.messages.append((MultipartState.PART_BEGIN, b""))

    def on_part_data(self, data, start, end):
        self.messages.append((MultipartState.PART_DATA, data[start:end]))

    def on_part_end(self):
        self.messages.append((MultipartState.PART_END, b""))

    def on_header_begin(self):
        self.messages.append((MultipartState.HEADER_BEGIN, b""))

    def on_header_field(self, data, start, end):
        self.messages.append((MultipartState.HEADER_FIELD, data[start:end]))

    def on_header_value(self, data, start, end):
        self.messages.append((MultipartState.HEADER_VALUE, data[start:end]))

    def on_header_end(self):
        self.messages.append((MultipartState.HEADER_END, b""))

    def on_headers_finished(self):
        self.messages.append((MultipartState.HEADERS_FINISHED, b""))

    def on_end(self):
        self.messages.append((MultipartState.END, b""))

    def run(self):
        try:
            boundary = self.parameters.get(b'boundary')
        except KeyError as e:
            raise ParseException("必须提供boundary")
        parser = multipart.MultipartParser(boundary, self.callbacks)
        parser.write(self._stream)
        parser.finalize()
        header_field = b""  # 头部字段
        header_value = b""  # 头部值
        content_disposition = None
        content_type = b""
        field_name = ""  # 这是字段名字
        data = b""
        file = None  # 文件
        items = []
        item_headers = []

        for msg_type, msg_data in self.messages:
            if msg_type == MultipartState.PART_BEGIN:
                content_disposition = None
                content_type = b""
                data = b""
                item_headers = []
            elif msg_type == MultipartState.HEADER_FIELD:
                header_field += msg_data
            elif msg_type == MultipartState.HEADER_VALUE:
                header_value += msg_data
            elif msg_type == MultipartState.HEADER_END:
                field = header_field.lower()
                if field == b"content-disposition":
                    content_disposition = header_value
                elif field == b"content-type":
                    content_type = header_value
                item_headers.append((field, header_value))
                header_field = b""
                header_value = b""
            elif msg_type == MultipartState.HEADERS_FINISHED:
                disposition, options = multipart.multipart.parse_options_header(content_disposition)
                try:
                    field_name = options[b"name"].decode(self.charset)
                except KeyError:
                    raise ParseException(
                        'The Content-Disposition header field "name" must be '
                        "provided."
                    )
                # 此处如果该字段是文件 那么就实例化SpooledUploadFile 否则将file置空
                if b"filename" in options:
                    filename = options[b"filename"].decode(self.charset)
                    file = SpooledUploadFile(
                        filename=filename,
                        content_type=content_type.decode(self.charset),
                        headers=item_headers,
                    )
                else:
                    file = None
            elif msg_type == MultipartState.PART_DATA:
                if file is None:
                    data += msg_data
                else:
                    file.write(msg_data)
            elif msg_type == MultipartState.PART_END:
                if file is None:
                    items.append((field_name, data))
                else:
                    file.seek(0)
                    items.append((field_name, file))

        return Form(items)


class FormParser:
    def __init__(self, stream):
        self.stream = stream
        self.callbacks = {
            "on_field_start": self.on_field_start,
            "on_field_name": self.on_field_name,
            "on_field_data": self.on_field_data,
            "on_field_end": self.on_field_end,
            "on_end": self.on_end,
        }
        self.messages = []

    def on_field_start(self) -> None:
        message = (FormState.FIELD_START, b"")
        self.messages.append(message)

    def on_field_name(self, data: bytes, start: int, end: int) -> None:
        message = (FormState.FIELD_NAME, data[start:end])
        self.messages.append(message)

    def on_field_data(self, data: bytes, start: int, end: int) -> None:
        message = (FormState.FIELD_DATA, data[start:end])
        self.messages.append(message)

    def on_field_end(self) -> None:
        message = (FormState.FIELD_END, b"")
        self.messages.append(message)

    def on_end(self) -> None:
        message = (FormState.END, b"")
        self.messages.append(message)

    def run(self):
        parser = multipart.QuerystringParser(self.callbacks)
        field_name = b""
        field_value = b""
        items = []
        parser.write(self.stream)
        parser.finalize()
        for message_type, message_bytes in self.messages:
            if message_type == FormState.FIELD_START:
                field_name = b""
                field_value = b""
            elif message_type == FormState.FIELD_NAME:
                field_name += message_bytes
            elif message_type == FormState.FIELD_DATA:
                field_value += message_bytes
            elif message_type == FormState.FIELD_END:
                name = unquote_plus(field_name.decode("latin-1"))
                value = unquote_plus(field_value.decode("latin-1"))
                items.append((name, value))

        return Form(items)
