class HTTPException(Exception):
    pass


class MethodNotAllowed(HTTPException):
    def __init__(self, method, allowed_methods):
        self.method = method
        self.allowed_methods = allowed_methods


class NotFound(HTTPException):
    pass
