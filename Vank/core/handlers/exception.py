from Vank.core.http.status import *
from Vank.core.http.response import Response
from Vank.core.exceptions import *
from peewee import (
    DataError,
    InternalError,
    InterfaceError,
    DatabaseError,
    IntegrityError,
    OperationalError,
    ProgrammingError,
    NotSupportedError
)


#
#
# def dump_response(data: dict):
#     return json.dumps(data).encode()
#
#
# def HttpNotFound(request):
#     code = HTTP_404_NOT_FOUND
#
#     error = {
#         'error': '请求路径有误',
#         'code': code
#     }
#     return Response404(error)
#
#
# def Http_MethodNotAllowed(request):
#     code = HTTP_405_METHOD_NOT_ALLOWED
#     error = {
#         'error': '请求方法不允许',
#         'code': code
#     }
#     return Response405(error)

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
