import inspect

_coroutine_function_mark = object()


def mark_coroutine_function(obj):
    """
    Force mark a function to be coroutine function whether this object is or not
    :param obj:
    :return: nothing
    """
    if hasattr(inspect, "markcoroutinefunction"):
        inspect.markcoroutinefunction(obj)
    else:
        setattr(obj, "_coroutine_function_mark", _coroutine_function_mark)


def is_coroutine_function(obj) -> bool:
    """
    Check if a function is coroutinefunction
    :param obj:
    :return: boolean
    """
    return inspect.iscoroutinefunction(obj) or getattr(obj, "_coroutine_function_mark", False)
