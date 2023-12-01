from vank.core.view import View
from vank.core.context.current import request
from vank.applications.static import control as ct


class StaticView(View):
    """
    处理静态文件视图
    """

    def get(self, fp, *args, **kwargs):  # noqa
        if_modify_since = request.headers.get('IF_MODIFIED_SINCE', None)
        response = ct.get_file(if_modify_since, fp)
        return response
