from Vank.core.http.status import *
from Vank.core.http.response import Response
from Vank.core.exceptions import *

def default_handler(request, exec):
    if isinstance(exec, NotFoundException):
        errors = {
            'error': exec.description
        }
        return Response(request, errors, status=HTTP_404_NOT_FOUND)

    if isinstance(exec, MethodNotAllowedException):
        errors = {
            'error': exec.description
        }
        return Response(request, errors, status=HTTP_405_METHOD_NOT_ALLOWED)

    if isinstance(exec, IntegrityError):
        errors = {
            'error': '数据库发生错误'
        }
        return Response(request, errors, status=HTTP_405_METHOD_NOT_ALLOWED)
    return Response(request, '服务器发生了错误', status=HTTP_500_INTERNAL_SERVER_ERROR)
