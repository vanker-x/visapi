import uuid
from datetime import datetime


class Convertor:
    regex: str = None

    def to_python(self, value):
        raise NotImplementedError("Subclass must implement to_python method")

    def to_url(self, value):
        raise NotImplementedError("Subclass must implement to_url method")


class IntConvertor(Convertor):
    regex = r"-?\d+"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return str(value)


class FloatConvertor(Convertor):
    regex = r"-?(?:\d+(?:\.\d*)?|\.\d+)"

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)


class StrConvertor(Convertor):
    # Match any non-empty string without slashes
    regex = r"[^/]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class SlugConvertor(Convertor):
    # Match a slug consisting of letters, numbers, hyphens, and underscores
    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class UUIDConvertor(Convertor):
    # Match a UUID string
    regex = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)


class BoolConvertor(Convertor):
    regex = r"true|false|1|0"

    def to_python(self, value):
        if value.lower() in ['true', '1']:
            return True
        elif value.lower() in ['false', '0']:
            return False
        else:
            raise ValueError("Invalid boolean value")

    def to_url(self, value):
        return 'true' if value else 'false'


class DateConvertor(Convertor):
    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d').date()

    def to_url(self, value):
        return value.strftime('%Y-%m-%d')


class PathConvertor(Convertor):
    regex = r"[^/].*?"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
