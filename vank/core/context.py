import math
import operator
import typing as t
from contextvars import ContextVar
from vank.core.http.request import Request

unbound = object()


class NotBoundError(Exception):
    ...


def not_bound_yet(obj: "ContextProxy"):
    """
    这是ContextProxy上下文代理没有找到被代理的对象时引发的LookUpError后的处理机制
    :param obj:
    :return:
    """
    return f"{obj._context_proxy_name} 暂未绑定上下文"  # noqa


def context_proxy_method(func: t.Callable, on_failed: t.Optional[t.Callable] = None):
    """
    通过func来操作被代理的对象，以保持原有对象的特性
    :param on_failed:
    :param func:
    :return:
    """

    def inner(self, *args, **kwargs):
        """
        有以下两种情况会出现获取到unbound对象的情况
        1.在没有上下文的情况下试图获取被代理的对象
        2.有上下文的情况下，由于ContextVar是线程安全的,但是别的线程试图获取当前线程的上下文,
        例如debug模式下,debugger试图获取ContextVar的数据,而debugger并不在当前线程。
        """
        obj = self._wrapped.get()
        if obj is not unbound:
            return func(obj, *args, **kwargs)
        if on_failed is None:
            raise NotBoundError(f"未找到上下文，请在上下文中执行")
        return on_failed(self, *args, **kwargs)

    return inner


class ContextProxy:
    """
    这是ContextVar的代理,他将自动完成ContextVar get方法
    你可以像使用被代理的那个对象一样使用这个代理
    """

    def __init__(self, name: str, wrapped: ContextVar):
        self._context_proxy_name = name
        self._wrapped = wrapped

    def __getattr__(self, item):
        if item in ["_context_proxy_name", "_wrapped"]:
            return object.__getattribute__(self, item)
        return context_proxy_method(getattr)(self, item)

    def __setattr__(self, key, value):
        if key in ["_context_proxy_name", "_wrapped"]:
            object.__setattr__(self, key, value)
            return
        return context_proxy_method(setattr)(self, key, value)

    __iter__ = context_proxy_method(iter)
    __add__ = context_proxy_method(operator.add)
    __dir__ = context_proxy_method(dir)
    __repr__ = context_proxy_method(repr, on_failed=not_bound_yet)
    __str__ = context_proxy_method(str)
    __divmod__ = context_proxy_method(divmod)
    __bytes__ = context_proxy_method(bytes)
    __format__ = context_proxy_method(format)
    __lt__ = context_proxy_method(operator.lt)
    __le__ = context_proxy_method(operator.le)
    __eq__ = context_proxy_method(operator.eq)
    __ne__ = context_proxy_method(operator.ne)
    __gt__ = context_proxy_method(operator.gt)
    __ge__ = context_proxy_method(operator.ge)
    __hash__ = context_proxy_method(hash)
    __bool__ = context_proxy_method(bool)
    __len__ = context_proxy_method(len)
    __getitem__ = context_proxy_method(operator.getitem)
    __setitem__ = context_proxy_method(operator.setitem)
    __delitem__ = context_proxy_method(operator.delitem)
    __next__ = context_proxy_method(next)
    __reversed__ = context_proxy_method(reversed)
    __contains__ = context_proxy_method(operator.contains)
    __sub__ = context_proxy_method(operator.sub)
    __mul__ = context_proxy_method(operator.mul)
    __matmul__ = context_proxy_method(operator.matmul)
    __truediv__ = context_proxy_method(operator.truediv)
    __floordiv__ = context_proxy_method(operator.floordiv)
    __mod__ = context_proxy_method(operator.mod)
    __pow__ = context_proxy_method(pow)
    __lshift__ = context_proxy_method(operator.lshift)
    __rshift__ = context_proxy_method(operator.rshift)
    __and__ = context_proxy_method(operator.and_)
    __xor__ = context_proxy_method(operator.xor)
    __or__ = context_proxy_method(operator.or_)
    __neg__ = context_proxy_method(operator.neg)
    __pos__ = context_proxy_method(operator.pos)
    __abs__ = context_proxy_method(abs)
    __invert__ = context_proxy_method(operator.invert)
    __complex__ = context_proxy_method(complex)
    __int__ = context_proxy_method(int)
    __float__ = context_proxy_method(float)
    __index__ = context_proxy_method(operator.index)
    __round__ = context_proxy_method(round)
    __trunc__ = context_proxy_method(math.trunc)
    __floor__ = context_proxy_method(math.floor)
    __ceil__ = context_proxy_method(math.ceil)
    # 使用lambda匿名函数来调用object
    __call__ = context_proxy_method(lambda obj, *args, **kwargs: obj(*args, **kwargs))
    # isinstance 将会触发__instancecheck__
    __instancecheck__ = context_proxy_method(lambda obj, other: isinstance(other, obj))
    __subclasscheck__ = context_proxy_method(lambda obj, other: issubclass(other, obj))
    __class__ = property(
        context_proxy_method(lambda obj: type(obj), on_failed=not_bound_yet))


# 线程安全的request ContextVar
_request_context_var = ContextVar("request", default=unbound)
# 被代理后的request ContextVar
request: Request = ContextProxy("request", _request_context_var)  # noqa

_application_context_var = ContextVar("application", default=unbound)
application = ContextProxy("application", _application_context_var)
