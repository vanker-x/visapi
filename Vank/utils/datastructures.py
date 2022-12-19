import tempfile


class SpooledUploadFile:
    """
    利用内置库tempfile的SpooledTemporaryFile;当文件超过特定大小时，将其写到磁盘
    """

    def __init__(self, filename, content_type, headers):
        self.filename = filename
        self.content_type = content_type
        self.headers = headers
        self.file = tempfile.SpooledTemporaryFile(max_size=1024 * 1024)

    def write(self, data: bytes):
        self.file.write(data)

    def read(self, size: int = -1) -> bytes:
        return self.file.read(size)

    def seek(self, offset):
        self.file.seek(offset)

    def close(self):
        self.file.close()

    def tell(self):
        return self.file.tell()

    def __str__(self):
        return f'<{self.__class__.__name__}>:{self.filename}'

    def __repr__(self):
        return f'<{self.__class__.__name__}>:{self.filename}'


class Form:
    def __init__(self, *args, ):
        if args:
            self._dict = {k: v for k, v in args[0]}
        else:
            self._dict = {}

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def close(self):
        [item.close() for item in self.values() if isinstance(item, SpooledUploadFile)]

    def __str__(self):
        return f"<{self.__class__.__name__}>:({self.items()})"

    def __repr__(self):
        return f"<{self.__class__.__name__}>:({self.items()})"
