import typing as t
from contextvars import ContextVar

from vank.core.context.base import unbound, ContextProxy

if t.TYPE_CHECKING:
    from vank.core.app import Application
    from vank.core.http.request import Request

# 线程安全的request ContextVar
_request_context_var = ContextVar("request", default=unbound)
# 被代理后的request ContextVar
request: "Request" = ContextProxy("request", _request_context_var)  # noqa

_application_context_var = ContextVar("application", default=unbound)
application: "Application" = ContextProxy("application", _application_context_var)  # noqa
