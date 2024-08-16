from tempfile import SpooledTemporaryFile


class FormFile:

    def __init__(self, filename, headers, content_type, max_size=1024 * 1024):
        self.headers = headers
        self.filename = filename
        self.content_type = content_type
        self.spooled_max_size = max_size
        self.file = SpooledTemporaryFile(max_size=self.spooled_max_size)

    def __del__(self):
        self.file.close()

    def __repr__(self):
        return f"<{self.__class__.__name__}>:{self.filename}"




class MultiValueDict(dict):
    def __init__(self, mapping_tuple=(), /, **kwargs):
        super().__init__()
        for key, value in mapping_tuple:
            self.append_value(key, value)
        for key, value in kwargs.items():
            self.append_value(key, value)

    def get(self, key, default=None):
        """
        return the first one if exists else default
        :param key:
        :param default:
        :return:
        """
        return super().get(key, [default])[0]

    def get_list(self, key, default=None):
        """
        return the whole list if exists else []
        :param key:
        :param default:
        :return:
        """
        return super().get(key, default) or []

    def append_value(self, key, value, error=False):
        """
        append a value to the list
        :param key:
        :param value:
        :param error:
        :return:
        """
        try:
            val = super().__getitem__(key)
        except Exception as e:
            if error:
                raise
            super().__setitem__(key, [value])
        else:
            val.append(value)

    def __setitem__(self, key, value):
        return super().__setitem__(key, [value])

    def __getitem__(self, item):
        val = super().__getitem__(item)
        try:
            return val[0]
        except IndexError:
            return val

    def __repr__(self):
        return f"<{self.__class__.__name__}: {super().__repr__()}>"


class QueryString(MultiValueDict):
    """

    """


class Form(MultiValueDict):
    pass


