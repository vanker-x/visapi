import math
import operator
import typing as t
from contextvars import ContextVar

if t.TYPE_CHECKING:
    from visapi.app import VisAPI
    from visapi.interface.asgi.http import Request as ASGIRequest
    from visapi.interface.rsgi.http import Request as RSGIRequest


class EmptyContextVar:
    def __init__(self, ctxv_name):
        self.ctxv_name = ctxv_name

    def __repr__(self):
        return f"Context variable '{self.ctxv_name}' not bound yet"

    def __str__(self):
        return f"Context variable '{self.ctxv_name}' not bound yet"


def proxy_method(method: t.Callable):
    def inner(self, *args, **kwargs):
        real = self._ctxv_obj.get()
        return method(real, *args, **kwargs)

    return inner


class ContextWrapper:
    def __init__(self, obj: ContextVar, ):
        object.__setattr__(self, "_ctxv_obj", obj)

    def __getattr__(self, item):
        if item in ["_ctxv_obj", "_ctxv_name"]:
            return self.__getattribute__(item)

        return proxy_method(getattr)(self, item)

    __iter__ = proxy_method(iter)
    __add__ = proxy_method(operator.add)
    __dir__ = proxy_method(dir)
    __repr__ = proxy_method(repr)
    __str__ = proxy_method(str)
    __divmod__ = proxy_method(divmod)
    __bytes__ = proxy_method(bytes)
    __format__ = proxy_method(format)
    __lt__ = proxy_method(operator.lt)
    __le__ = proxy_method(operator.le)
    __eq__ = proxy_method(operator.eq)
    __ne__ = proxy_method(operator.ne)
    __gt__ = proxy_method(operator.gt)
    __ge__ = proxy_method(operator.ge)
    __hash__ = proxy_method(hash)
    __bool__ = proxy_method(bool)
    __len__ = proxy_method(len)
    __getitem__ = proxy_method(operator.getitem)
    __setitem__ = proxy_method(operator.setitem)
    __delitem__ = proxy_method(operator.delitem)
    __next__ = proxy_method(next)
    __reversed__ = proxy_method(reversed)
    __contains__ = proxy_method(operator.contains)
    __sub__ = proxy_method(operator.sub)
    __mul__ = proxy_method(operator.mul)
    __matmul__ = proxy_method(operator.matmul)
    __truediv__ = proxy_method(operator.truediv)
    __floordiv__ = proxy_method(operator.floordiv)
    __mod__ = proxy_method(operator.mod)
    __pow__ = proxy_method(pow)
    __lshift__ = proxy_method(operator.lshift)
    __rshift__ = proxy_method(operator.rshift)
    __and__ = proxy_method(operator.and_)
    __xor__ = proxy_method(operator.xor)
    __or__ = proxy_method(operator.or_)
    __neg__ = proxy_method(operator.neg)
    __pos__ = proxy_method(operator.pos)
    __abs__ = proxy_method(abs)
    __invert__ = proxy_method(operator.invert)
    __complex__ = proxy_method(complex)
    __int__ = proxy_method(int)
    __float__ = proxy_method(float)
    __index__ = proxy_method(operator.index)
    __round__ = proxy_method(round)
    __trunc__ = proxy_method(math.trunc)
    __floor__ = proxy_method(math.floor)
    __ceil__ = proxy_method(math.ceil)
    __call__ = proxy_method(lambda obj, *args, **kwargs: obj(*args, **kwargs))
    __instancecheck__ = proxy_method(isinstance)
    __subclasscheck__ = proxy_method(issubclass)
    __class__ = property(proxy_method(lambda obj: obj.__class__))


application: "VisAPI" = ContextWrapper(ContextVar("application", default=EmptyContextVar("application")), )  # noqa
request: t.Union["ASGIRequest", "RSGIRequest"] = \
    ContextWrapper(ContextVar("request", default=EmptyContextVar("application")))  # noqa
