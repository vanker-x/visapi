import inspect
import typing as t
from types import MappingProxyType


def _get_object_argument_inspections(obj) -> MappingProxyType[str, inspect.Parameter]:
    return inspect.signature(obj).parameters


def has_key_word_argument(obj) -> bool:
    """
    检测接收的参数中是否含有类型为关键字可变参数
    :param obj:
    :return:
    """
    for key, value in _get_object_argument_inspections(obj).items():
        if value.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def has_var_positional_argument(obj) -> bool:
    """
    检测接收的参数中是否含有类型为可变参数
    :param obj:
    :return:
    """
    for key, value in _get_object_argument_inspections(obj).items():
        if value.kind == inspect.Parameter.VAR_POSITIONAL:
            return True
    return False


def contain_arguments(obj, names: t.List[str]) -> bool:
    """
    检测接收的参数是否为names的超集
    :param names:
    :param obj:
    :return:
    """
    return set(_get_object_argument_inspections(obj).keys()).issuperset(names)


def has_argument(obj, name: str) -> bool:
    """
    检测接收的参数中是否含有name
    :param obj:
    :param name:
    :return:
    """
    return contain_arguments(obj, [name])
