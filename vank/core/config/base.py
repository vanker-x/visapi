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


def check_secret_key(sender, *args, **kwargs):
    """检查secret_key"""
    try:
        secret = getattr(sender, 'SECRET_KEY', None)
    except AttributeError:
        raise Exception('配置中未找到SECRET_KEY')
    if not isinstance(secret, str):
        raise Exception(f'配置中SECRET_KEY必须为字符串而不是 {type(secret).__name__}')
    if not len(secret) > 15:
        raise Exception('配置中SECRET_KEY的长度必须大于15位')


def check_static_url(sender, *args, **kwargs):
    """检查静态路径"""
    try:
        url = getattr(sender, "STATIC_URL", None)
    except AttributeError:
        raise Exception('配置中未找到STATIC_URL')
    if not isinstance(url, str):
        raise Exception(f'配置中STATIC_URL必须为字符串而不是 {type(url).__name__}')
    if not url.startswith('/') and not url.endswith('/'):
        raise Exception('STATIC_URL的开头和结尾必须为"/"')
