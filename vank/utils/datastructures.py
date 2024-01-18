import tempfile
import typing as t
from itertools import chain


class SpooledUploadFile:
    """
    Specialized to switch BytesIO or StringIO to a real file when it exceeds max_size
    """

    def __init__(self, filename, content_type, headers):
        self.filename = filename
        self.content_type = content_type
        self.headers = headers
        self.file = tempfile.SpooledTemporaryFile(max_size=1024 * 1024)

    def write(self, data: bytes):
        """
        Proxy method for SpooledTemporaryFile.write
        :param data: byte data
        :return:
        """
        self.file.write(data)

    def read(self, size: int = -1) -> bytes:
        """
        Proxy method for SpooledTemporaryFile.read
        :param size:
        :return:
        """
        return self.file.read(size)

    def seek(self, offset: int, whence: t.Optional[int] = 0):
        """
        Proxy method for SpooledTemporaryFile.seek
        :param offset: same as BytesIO
        :param whence: same as BytesIO
        :return:
        """
        self.file.seek(offset, whence)

    def close(self):
        """
        Proxt method for SpooledTemporaryFile.close
        :return:
        """
        self.file.close()

    def tell(self):
        """
        Return the current position.
        :return:
        """
        return self.file.tell()

    def __str__(self):
        return f'<{self.__class__.__name__}>:{self.filename}'

    def __repr__(self):
        return f'<{self.__class__.__name__}>:{self.filename}'


class MultiValueDict(dict):
    def __init__(self, raw: t.Optional[t.Iterable] = None, /, **kwargs):
        if raw:
            if not isinstance(raw, (list, tuple, set)):
                raise ValueError("positional only argument must be (key, value) pairs of list, tuple or set")
            [self[key].append(val) for key, val in raw]
        [self[key].append(val) for key, val in kwargs.items()]

    def get(self, key, default=None):
        if not (data := self[key]):
            return default
        return data[-1]

    def get_all(self, key, default=None):
        if not (data := self[key]):
            return default
        return data

    def append(self, key, value):
        self[key].append(value)
        return self

    def pop_value(self, key, index):
        return self[key].pop(index)

    def __setitem__(self, key, value):
        super().__setitem__(key, [value] if not isinstance(value, (list, tuple, set)) else [*value])

    def __missing__(self, key):
        self[key] = []
        return self[key]

    def __repr__(self):
        return f"{self.__class__.__name__}:{super().__repr__()}"

    def __str__(self):
        return f"{self.__class__.__name__}:{super().__str__()}"


class Form(MultiValueDict):
    """
    form表单
    """

    def close(self):
        [item.close() for item in chain(*self.values()) if isinstance(item, SpooledUploadFile)]


class QueryString(MultiValueDict):
    """查询参数"""
    pass


class Headers:
    def __init__(self, raw_headers=None):
        self._list = []
        if raw_headers:
            self._list = [(key.encode('latin-1'), value.encode('latin-1')) for key, value in raw_headers]

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

    def setdefault(self, key, default):
        # not in self 会调用__contains__魔术方法
        if key not in self:
            self._list.append((key.encode('latin-1'), default.encode('latin-1')))
            return default
        else:
            return self.get(key)

    def update(self, key, value):
        for index, item in enumerate(self._list):
            if item[0].decode('latin-1').lower() == key.lower():
                self._list[index] = (key.encode('latin-1'), value.encode('latin-1'))

    def remove(self, key):
        # 使用[:]可以创建一个新的对象
        for idx, item in enumerate(self._list[:]):
            if item[0].decode('latin-1').lower() == key.lower():
                self._list.pop(idx)

    def __contains__(self, key):
        res = [item_key for item_key, value in self.items() if item_key.lower() == key.lower()]
        return any(res)

    def __str__(self):
        return f'<{self.__class__.__name__}>:{self.items()}'

    def __repr__(self):
        return f'<{self.__class__.__name__}>:{self.items()}'


class Session:
    def __init__(self, session=None):
        self._session = session or {}
        self._is_changed = False  # session是否修改的标志 SessionMiddleware的handle_response会用到

    def __getitem__(self, key):
        if key in self._session.keys():
            return self._session[key]
        raise KeyError(f'Session key "{key}" does not exist')

    def __delitem__(self, key):
        if key in self.keys():
            del self._session[key]
            self._is_changed = True
        else:
            raise KeyError(f'Unable to delete session key."{key}" does not exist')

    def __setitem__(self, key, value):
        self._session[key] = value
        self._is_changed = True

    def __bool__(self):
        return bool(self._session)

    def get(self, key, default=None):
        return self._session.get(key, default)

    def add(self, key, value):
        self._session[key] = value
        self._is_changed = True

    def keys(self):
        return self._session.keys()

    def values(self):
        return self._session.values()

    def items(self):
        return self._session.items()

    def pop(self, key, default=None):
        if key in self.keys():
            value = self._session.pop(key)
            self._is_changed = True
            return value
        else:
            return default

    def setdefault(self, key, value):
        if key in self.keys():
            return self._session[key]
        else:
            self._session[key] = value
            self._is_changed = True
            return value

    def update(self, dict_obj: dict):
        self._session.update(dict_obj)
        self._is_changed = True

    def clear(self):
        self._session = {}
        self._is_changed = True

    def delete(self, key):
        del self[key]

    @property
    def raw(self):
        return self._session

    @property
    def is_changed(self):
        return self._is_changed

    def __str__(self):
        return f'<{self.__class__.__name__}>:{self.items()}'

    def __repr__(self):
        return f'<{self.__class__.__name__}>:{self.items()}'
