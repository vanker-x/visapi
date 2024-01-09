from vank.core.context.current import request, application
from vank.applications.static import control as ct


def handle_static_file(fp):
    if_modify_since = request.headers.get('IF_MODIFIED_SINCE', None)
    return ct.get_file(if_modify_since, fp)
