import multipart
import enum


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


class ParseException(Exception):
    """
    解析时异常
    """


class MultiPartParser:
    def __init__(self, content_type, parameters, stream):
        self.content_type = content_type
        self.parameters = parameters
        self._stream = stream
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
            boundary = self.parameters.get('boundary')
        except KeyError as e:
            raise ParseException("必须提供boundary")
        parser = multipart.MultipartParser(boundary, self.callbacks)
        parser.write(self._stream)
        for msg_type, msg_data in self.messages:
            print(msg_type)

        return
