# @FileName: base.py
# @Date    : 2022/9/7-1:17
# @Author  : Vank
# @Project : Vank


class BaseMiddleware:
    """
    中间件基类
    实例方法:
        1.handle_request 在接收到请求时调用
        2.handle_view 在进入处理函数之前调用
        3.handle_response 在处理函数之后调用 必须返回response
        这三个实例方法应该被子类重写

    """

    def __init__(self, get_response_callable):
        """

        :param get_response_callable: 为一个可调用对象 用于获取响应
        """

        self.get_response_callable = get_response_callable

    def handle_request(self, request):
        """
        在接收到请求时 调用此方法
        :param request: BasicRequest
        :return: 返回None 继续执行下一个中间件  返回Response 则直接返回到客户端
        """
        return None

    def handle_view(self, request, view_func, **view_kwargs):
        """
        在进入视图之前调用此方法
        :param request: BasicRequest
        :param view_func: 对应的视图函数
        :param view_kwargs: 对应的视图函数所需可变参数
        :return: 返回None 继续执行下一个中间件  返回Response 则直接返回到客户端
        """
        return None

    def handle_response(self, request, response):
        """
        在视图函数处理该请求之后调用此方法
        :param request: BasicRequest
        :param response: BasicResponse
        :return: 此方法应当始终返回 response
        """
        return response

    def __call__(self, request):
        response = None
        # 处理请求
        if hasattr(self, 'handle_request'):
            response = self.handle_request(request)
        # 交给对应的函数处理
        if not response:
            response = self.get_response_callable(request)

        # 处理response
        if hasattr(self, 'handle_response'):
            response = self.handle_response(request, response)

        return response


class A(BaseMiddleware):
    def handle_request(self, request):
        return None

    def handle_view(self, request, view_func, **view_kwargs):
        pass

    def handle_response(self, request, response, ):
        return response
