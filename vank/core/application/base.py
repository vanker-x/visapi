from vank.core.config import conf
from vank.utils import import_from_str
from vank.utils.locator import get_obj_file
from vank.middleware.base import Middleware
from vank.utils.log import setup_config as setup_log_config
from vank.core.handlers.exception import conv_exc_to_response
from vank.utils.arguments import only_accept_argument, accept_variable_argument


class MiddlewareAppMixin:
    """
    Middleware Application Mixin
    """

    def __init__(self):
        self.entry_point = None
        self.error_converter = import_from_str(conf.ERROR_CONVERTER)
        self.setup()

    def setup(self):
        setup_log_config(conf.LOGGING)
        self.init_middleware()

    def finalize(self, *args, **kwargs):
        raise NotImplemented("sub class should implement this method")

    def init_middleware(self):
        if (
                not only_accept_argument(self.error_converter, "exc")
                and
                not accept_variable_argument(self.error_converter)
        ):
            raise ValueError(f"ERROR_CONVERTER must receive exc parameter or"
                             f" variable parameter like *args or **kwargs at file {get_obj_file(self.error_converter)}")
        wrapped_func = conv_exc_to_response(self.finalize, self.error_converter)
        for path in reversed(conf.MIDDLEWARES):
            cls = import_from_str(path)
            if not issubclass(cls, Middleware):
                raise ValueError(f'"%s" Should be a subclass of "Middleware" instead of %s' % (
                    path,
                    type(cls).__name__
                ))
            wrapped_func = conv_exc_to_response(cls(wrapped_func), self.error_converter)
        self.entry_point = wrapped_func
