# @FileName: load_module.py
# @Date    : 2022/9/7-1:54
# @Author  : vank
# @Project : vank
import re
import traceback
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
        raise ValueError('请传入正确语法的模块路径\n'
                         'e.g:vank.utils.load_module:import_from_str')
    module, attr = res.groupdict().values()
    try:
        module_object = import_module(module)
        if attr:
            return getattr(module_object, attr)
        return module_object
    except Exception as e:
        raise ImportError(f'导入{import_str}失败,请传入正确语法的模块路径\n'
                          f'ERROR:{traceback.format_exc()}')
