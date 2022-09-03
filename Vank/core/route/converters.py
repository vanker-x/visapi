class BasicConverter:
    def __init__(self, regex):
        self.regex = regex

    def convert(self, value):
        pass


# 数字转换器
class IntConverter(BasicConverter):
    def __init__(self):
        regex = r"\d+"
        super(IntConverter, self).__init__(regex)

    def convert(self, value):
        return int(value)


# 字符串转换器
class StrConverter:
    def __init__(self):
        regex = r'[a-zA-Z0-9]+'
        super(StrConverter, self).__init__(regex)

    def convert(self, value):
        return str(value)


# 浮点数转换器
class FloatConverter(BasicConverter):
    def __init__(self):
        regex = r"\d+\.\d+"
        super(FloatConverter, self).__init__(regex)

    def convert(self, value):
        return float(value)


class EmailConverter(BasicConverter):
    def __init__(self):
        regex = r'[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+'
        super(EmailConverter, self).__init__(regex)

    def convert(self, value):
        return str(value)
