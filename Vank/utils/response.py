# Created by Vank
# DateTime: 2022/11/15-16:04
# Encoding: UTF-8

import mimetypes


def get_mimetype(suffix: str, default=None):
    """
    根据文件后缀获取对应的mimetype
    :param suffix: 导入路径
    :param default: 缺省参数
    :return: str
    """
    if not suffix.startswith('.'):
        suffix = f'.{suffix}'

    return mimetypes.types_map.get(suffix, default)

