import inspect


class InspectError(Exception):
    """
    检查错误
    """


def get_func_parameters(func):
    """
    获取函数的所有所需参数
    """
    args = [arg for arg in inspect.signature(func).parameters.values()]
    return args


def func_has_args(func, ignore_first=False):
    """
    函数是否有参数 如果func为method 那么请设置ignore_first 为True
    否则不会排除method的self
    """
    args = get_func_parameters(func)
    if ignore_first and args:
        args = args[1:]
    return bool(args)


def func_accept_variable_args(func):
    """
    函数是否接收可变参数(*args)
    """
    return any(
        parameter for parameter in get_func_parameters(func) if parameter.kind == inspect.Parameter.VAR_POSITIONAL)


def func_accept_variable_kwargs(func):
    """
    函数是否接收关键字参数(**kwargs)
    """
    return any(parameter for parameter in get_func_parameters(func) if parameter.kind == inspect.Parameter.VAR_KEYWORD)
