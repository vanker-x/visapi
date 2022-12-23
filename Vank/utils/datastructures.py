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


class Headers:
    def __init__(self, raw_headers=None):
        self._list = []
        if raw_headers:
            self._list = [(key.encode('latin-1'), value.encode('latin-1')) for key, value in raw_headers.items()]

    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, item: str):
        res = [value.decode('latin-1') for key, value in self._list if key.decode('latin-1').lower() == item.lower()]
        if res:
            return res[0]
        raise KeyError(item)

    def items(self):
        return [(key.decode('latin-1'), value.decode('latin-1')) for key, value in self._list]

    def keys(self):
        return [key.decode('latin-1') for key, value in self._list]

    def values(self):
        return [value.decode('latin-1') for key, value in self._list]

    def get(self, key, default=None):
        for item_key, value in self._list:
            if item_key.decode('latin-1').lower() == key.lower():
                return value.decode('latin-1')
        return default

    def add(self, key, value):
        self._list.append((key.encode('latin-1'), value.encode('latin-1')))

    def setdefault(self, key, value):
        # not in self 会调用__contains__魔术方法
        if key not in self:
            self._list.append((key.encode('latin-1'), value.encode('latin-1')))

    def update(self, key, value):
        for index, item in enumerate(self._list):
            if item[0].decode('latin-1').lower() == key.lower():
                self._list[index] = (key.encode('latin-1'), value.encode('latin-1'))
        else:
            self.setdefault(key, value)

    def __contains__(self, key):
        res = [item_key for item_key, value in self.items() if item_key.lower() == key.lower()]
        return any(res)
