# @FileName: load_module.py
# @Date    : 2022/9/7-1:54
# @Author  : vank
# @Project : vank
import re
from importlib import import_module

import_regex = re.compile(r'^(?P<module>[a-zA-Z]+[a-zA-Z0-9_]*(\.[a-zA-Z]+[a-zA-Z0-9_]*)*)(:(?P<attr>[a-zA-Z0-9_]+))?$')


def import_from_str(import_str: str):
    """
    导入模块、模块中的属性
    :param import_str: 导入路径
    :return: 类或属性
    e.g:
         vank.utils.load_module:import_from_str
    """
    res = import_regex.match(import_str)
    if not res:
        raise ValueError(f'wrong path syntax "{import_str}"\n'
                         'e.g:vank.utils.load_module:import_from_str')
    module, attr = res.groupdict().values()
    try:
        module_object = import_module(module)
        if attr:
            return getattr(module_object, attr)
        return module_object
    except Exception as e:
        raise ImportError(f'Failed to import "{import_str}". Please pass in the path with the correct syntax\n')
