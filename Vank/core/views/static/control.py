from pathlib import Path
from Vank.core.config import conf
from Vank.core.http.response import ResponseFile, Response
from Vank.core.http.request import Request
from Vank.core.exceptions import NotFoundException
from email.utils import parsedate_to_datetime


def _get_file_modified(gmt_date: str, file_mtime) -> bool:
    """
    判断http header的modify时间和当前文件的modify时间是否相等
    """
    try:
        gmt_timestamp = parsedate_to_datetime(gmt_date).timestamp()
    except:
        return True
    else:
        return int(gmt_timestamp) == int(file_mtime)


def get_file(request: "Request", fp):
    full_path = Path(conf.STATIC_PATH).joinpath(fp)
    # 判断文件是否存在
    if not full_path.exists():
        raise NotFoundException(f'{full_path}资源不存在')
    # 判断是否为文件夹
    if full_path.is_dir():
        raise NotFoundException('不允许索引目录')
    # 获取modify时间,如果没有修改那么不返回文件
    # https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/If-Modified-Since
    if_modify_since = request.headers.get('IF_MODIFIED_SINCE', None)
    if if_modify_since:
        last_modify_time = full_path.stat().st_mtime
        if _get_file_modified(if_modify_since, last_modify_time):
            return Response(status=304)
    return ResponseFile(filepath=full_path.as_posix())
