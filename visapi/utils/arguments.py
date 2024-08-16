import inspect
import typing as t
from types import MappingProxyType


def _get_object_argument_inspections(obj) -> MappingProxyType[str, inspect.Parameter]:
    return inspect.signature(obj).parameters


def accept_var_key_word_argument(obj: callable) -> bool:
    """
    Check if the parameters received by obj contain keyword variable parameter like **kwargs
    :param obj: callable
    :return: boolean
    """
    for key, value in _get_object_argument_inspections(obj).items():
        if value.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def accept_var_positional_argument(obj: callable) -> bool:
    """
    Check if the parameters received by obj contain variable positional parameter like *args
    :param obj: callable
    :return: boolean
    """
    for key, value in _get_object_argument_inspections(obj).items():
        if value.kind == inspect.Parameter.VAR_POSITIONAL:
            return True
    return False


def accept_variable_argument(obj: callable) -> bool:
    """
    Check if obj receives variable parameter like *args or **kwargs
    :param obj: callable
    :return: boolean
    """
    return accept_var_positional_argument(obj) and accept_var_positional_argument(obj)


def accept_arguments(obj: callable, names: t.List[str]) -> bool:
    """
    Check if the received parameters are a superset of names
    :param obj: callable
    :param names: a list of parameter string
    :return: boolean
    """
    return set(_get_object_argument_inspections(obj).keys()).issuperset(names)


def accept_argument(obj: callable, name: str) -> bool:
    """
    Check if the parameters received by obj contain name
    :param obj: callable
    :param name: accept argument name
    :return: boolean
    """
    return accept_arguments(obj, [name])


def only_accept_argument(obj: callable, name: str) -> bool:
    """
    Check if obj only accepts the name parameter
    :param obj: callable
    :param name: accept argument name
    :return: boolean
    """
    length = 2 if inspect.ismethod(obj) else 1
    return len(_get_object_argument_inspections(obj).keys()) == length and accept_argument(obj, name)
