import typing as t
from vank.core import conf
from vank.utils import import_from_str
from vank.core.routing.router import Router
from vank.core.application.base import MiddlewareAppMixin

ApplicationType = t.TypeVar("ApplicationType", Router, MiddlewareAppMixin)


class Application:
    """
    Instantiation application by APPLICATION_CLASS
    """

    def __new__(cls, *args, **kwargs) -> ApplicationType:
        app_class = import_from_str(conf.APPLICATION_CLASS)
        return app_class(*args, **kwargs)


class SubApplication(Router):
    def __init__(self, name: str, prefix: t.Optional[str] = None):
        super(SubApplication, self).__init__()
        self.name = name
        self.prefix = prefix
        if self.prefix:
            assert not self.prefix.endswith('/'), 'The Route prefix should not end with "/"'
            assert self.prefix.startswith('/'), 'The Route prefix should start with "/"'
        self.root: t.Optional[ApplicationType] = None
