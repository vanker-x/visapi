from Vank.core.views import View
from Vank.core.http.response import Response


class StaticView(View):

    def get(self, request, fp, *args, **kwargs):
        print(fp)
        return Response('这是静态文件路由')
