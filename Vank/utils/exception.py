# @FileName: exception.py
# @Date    : 2022/9/12-3:52
# @Author  : Vank
# @Project : Vank

def get_exception_reason(exception):
    """
    此方法用于获取异常的描述
    :param exception: Exception
    :return:
    """
    try:
        reason = exception.args[0]
        return reason if isinstance(reason, str) else '未知错误'
    except (AttributeError, IndexError):
        return '未知错误'
