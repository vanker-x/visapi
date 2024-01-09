# @FileName: init.py
# @Date    : 2023/1/27-1:28
# @Author  : vank
# @Project : vank
import sys
import time
import hashlib
import os.path
from vank.utils.cli import BaseCommand

settings_template = """
from pathlib import Path

PROJECT_BASE_DIR = Path(__file__).parent
# 密钥
SECRET_KEY = '%(secret)s'

# 子应用
SUB_APPLICATIONS = [
    'vank.applications.static.urls:sub',
]

# 含参数路由转换器
ROUTE_CONVERTERS = {
    'int': 'vank.core.routing.converters:IntConverter',
    'float': 'vank.core.routing.converters:FloatConverter',
    'email': 'vank.core.routing.converters:EmailConverter',
    'uuid': 'vank.core.routing.converters:UUIDConverter',
    'path': 'vank.core.routing.converters:PathConverter',
    'str': 'vank.core.routing.converters:StrConverter',
}

# 中间件
MIDDLEWARES = [
    'vank.middleware.session:SessionMiddleware'
]

# 指定Application
APPLICATION_CLASS = "vank.core.application.wsgi:WSGIApplication"

# 异常转换器
ERROR_CONVERTER = 'vank.core.handlers.exception:default_exception_converter'

# 静态文件URL
STATIC_URL = '/static'

# 静态文件存放路径
STATIC_PATH = PROJECT_BASE_DIR / 'statics'

# 静态文件路由端点
STATIC_ENDPOINT = 'static'

# 热重载
AUTO_RELOAD = True

# 热重载检测间隔
AUTO_RELOAD_INTERVAL = 1

# 主机地址
DEFAULT_HOST = '127.0.0.1'

# 端口号
DEFAULT_PORT = 5000

# 编码
DEFAULT_CHARSET = 'utf-8'

# Session的Cookie名称
SESSION_COOKIE_NAME = 'sessionid'

# Session的Cookie路径
SESSION_COOKIE_PATH = '/'

# Session的Cookie有效时间
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7

# Session的Cookie过期时间
SESSION_COOKIE_EXPIRES = SESSION_COOKIE_MAX_AGE

# Session的Cookie是否HTTP ONLY
SESSION_COOKIE_HTTP_ONLY = False

# lax strict none
SESSION_COOKIE_SAME_SITE = 'lax'

# SECURE
SESSION_COOKIE_SECURE = False

# 域
SESSION_COOKIE_DOMAIN = None

# 跨域允许的header
CORS_ALLOWED_HEADERS = ["*"]

# 跨域允许的method
CORS_ALLOWED_METHODS = ["*"]

# 跨域允许的origin
CORS_ALLOWED_ORIGINS = ["*"]

# 是否携带凭证
WITH_CREDENTIALS = True

# max-age
CORS_MAX_AGE = 500

"""
main_template = """
from vank.core import Application, request, response

app = Application()


@app.route('/', methods=['GET'])
def say_hi(*args, **kwargs):
    return response.ResponsePlain(f'Hi,your request path is {request.path}')


if __name__ == '__main__':
    app.start()

"""

init_templates = {
    'settings.py': settings_template,
    'main.py': main_template,
}


class Command(BaseCommand):
    description = 'Initialize the project through this command'

    def run(self, argv):
        options, args = self.parser.parse_known_args(argv[2:])
        project_name = options.name
        if project_name:
            project_dir = os.path.join(os.getcwd(), project_name)
            if os.path.exists(project_dir):
                self.stderr.write(f'The folder "{project_name}" already exists and cannot be created\n')
                sys.exit()
        else:
            project_dir = os.getcwd()
        os.makedirs(project_dir, exist_ok=True)
        variables = dict(
            secret=hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
        )
        for file_name, template in init_templates.items():
            with open(os.path.join(project_dir, file_name), 'w', encoding='utf-8') as f:
                f.write(template.lstrip() % variables)

    def init_arguments(self):
        self.parser.add_argument(
            '-n',
            '--name',
            help='Initialize the project in a new directory'
        )
