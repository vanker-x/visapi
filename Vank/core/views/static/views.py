from Vank.core.views import View
from Vank.core.views.static import control as ct


class StaticView(View):
    """
    处理静态文件视图
    """

    def get(self, request, fp, *args, **kwargs):  # noqa
        response = ct.get_file(request, fp)
        return response
