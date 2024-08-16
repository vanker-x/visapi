class Request:
    def __init__(self, scope, proto):
        self.scope = scope
        self.proto = proto

    @property
    def path(self):
        pass


class Response:
    pass
