# @FileName: init.py
# @Date    : 2023/1/27-1:28
# @Author  : Vank
# @Project : Vank
import sys
import os.path
from secrets import choice
from Vank.utils.cmd import BaseCommand

settings_template = """
from pathlib import Path

PROJECT_BASE_DIR = Path(__file__).parent
# 密钥
SECRET_KEY = '{secret_key}'

# 含参数路由转换器
ROUTE_CONVERTERS = {
    'int': 'Vank.core.routing.converters.IntConverter',
    'float': 'Vank.core.routing.converters.FloatConverter',
    'email': 'Vank.core.routing.converters.EmailConverter',
    'uuid': 'Vank.core.routing.converters.UUIDConverter',
    'path': 'Vank.core.routing.converters.PathConverter',
}

# 中间件
MIDDLEWARES = [
    'Vank.middleware.session.SessionMiddleware'
]

# 错误处理器
ERROR_HANDLER = 'Vank.core.handlers.exception.default_handler'

# 静态文件URL
STATIC_URL = '/static/'

#静态文件存放路径
STATIC_PATH = PROJECT_BASE_DIR / 'statics'

# 热重载
AUTO_RELOAD = True

# 热重载检测间隔
AUTO_RELOAD_INTERVAL = 1

AUTO_RELOAD_SPEC_SUFFIX = []

AUTO_RELOAD_IGNORE_SUFFIX = []

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

#域
SESSION_COOKIE_DOMAIN = None
"""
main_template = """
from Vank.core import Application
from Vank.core.http.response import Response

app = Application()


@app.new_route('/')
def say_hi(request, *args, **kwargs):
    return Response('Hi!')


if __name__ == '__main__':
    app.start()

"""

init_templates = {
    'settings.py': settings_template,
    'main.py': main_template,
}


class Command(BaseCommand):
    description = '通过init命令初始化项目'

    def run(self, argv):
        options, args = self.parser.parse_known_args(argv[2:])
        project_name = options.name
        if project_name:
            project_dir = os.path.join(os.getcwd(), project_name)
        else:
            project_dir = os.getcwd()
        os.makedirs(project_dir, exist_ok=True)

        for file_name, template in init_templates.items():
            with open(os.path.join(project_dir, file_name), 'w', encoding='utf-8') as f:
                f.write(template)

    def init_arguments(self):
        self.parser.add_argument(
            '-n',
            '--name',
            help='在新的目录下初始化项目'
        )
