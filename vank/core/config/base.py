# Created by vank
# DateTime: 2022/10/9-17:24
# Encoding: UTF-8


class BaseSettings:
    # 项目地址
    PROJECT_BASE_DIR = ""
    # 密钥
    SECRET_KEY = ""
    # 含参数路由转换器
    ROUTE_CONVERTERS = {}
    # 中间件
    MIDDLEWARES = []
    # 错误处理器
    ERROR_HANDLER = ""
    # 日志
    LOGGING = {}
    # 子应用
    SUB_APPLICATIONS = []

    # 处理静态文件(生产环境请设置为False)
    USE_STATIC = True

    # 静态文件URL
    STATIC_URL = ''

    # 静态文件存放路径
    STATIC_PATH = ""

    # 静态文件路由端点
    STATIC_ENDPOINT = ''

    # 热重载
    AUTO_RELOAD = True

    # 热重载检测间隔
    AUTO_RELOAD_INTERVAL = 1

    # 主机地址
    DEFAULT_HOST = ''

    # 端口号
    DEFAULT_PORT = 5000

    # 编码
    DEFAULT_CHARSET = ''

    # Session的Cookie名称
    SESSION_COOKIE_NAME = ''

    # Session的Cookie路径
    SESSION_COOKIE_PATH = ''

    # Session的Cookie有效时间
    SESSION_COOKIE_MAX_AGE = 0

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
    CORS_ALLOWED_HEADERS = []

    # 跨域允许的method
    CORS_ALLOWED_METHODS = []

    # 跨域允许的origin
    CORS_ALLOWED_ORIGINS = []

    # 是否携带凭证
    WITH_CREDENTIALS = True

    # max-age
    CORS_MAX_AGE = 500


def check_secret_key(sender, *args, **kwargs):
    """检查secret_key"""
    try:
        secret = getattr(sender, 'SECRET_KEY', None)
    except AttributeError:
        raise Exception('SECRET_KEY not found in configuration')
    if not isinstance(secret, str):
        raise Exception(f'The SECRET_KEY type in the configuration must be str instead of {type(secret).__name__}')
    if not len(secret) > 15:
        raise Exception('The length of SECRET_KEY in the configuration must >= 15')


def check_static_url(sender, *args, **kwargs):
    """检查静态路径"""
    try:
        url = getattr(sender, "STATIC_URL", None)
    except AttributeError:
        raise Exception('STATIC_URL not found in configuration')
    if not isinstance(url, str):
        raise Exception(f'The STATIC_URL type in the configuration must be str instead of {type(url).__name__}')
    if not url.startswith('/') and not url.endswith('/'):
        raise Exception('The start and end of the STATIC_URL must be "/"')
