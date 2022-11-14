# @FileName: load_module.py
# @Date    : 2022/9/7-1:54
# @Author  : Vank
# @Project : Vank
from importlib import import_module


def import_from_str(import_str: str):
    """
    导入一个模块中的类或属性
    :param import_str: 导入路径
    :return: 类或属性
    """
    try:
        module, att_or_class = import_str.rsplit('.', 1)
        return getattr(import_module(module), att_or_class)
    except Exception as e:
        raise ImportError(f'导入{import_str}失败,路径应该用.分开 例如 Vank.utils.load_module.import_from_str')
