# 配置
通过设置不同的配置,可以控制应用程序的行为。  
在启动服务时`vank`默认加载与程序入口点([最高代码环境](https://docs.python.org/zh-cn/3/library/__main__.html#what-is-the-top-level-code-environment))同级目录下的settings.py里的配置。
如果你想为`vank`指定配置所在位置,请看[指定配置](#_2)。
### SECRET_KEY(密钥)

默认值: **' '(空字符串)**  
这是一个密钥,用于提供签名服务并且它是随机的,所以你不应该将它暴露给外部
***
### SUB_APPLICATIONS(子应用)
默认值:

```python
[
    'vank.applications.static.urls:sub',
]
```
所挂载的子应用
***
### ROUTE_CONVERTERS(路由转换器)

默认值:

```python
{
    'int': 'vank.core.routing.converters:IntConverter',
    'float': 'vank.core.routing.converters:FloatConverter',
    'email': 'vank.core.routing.converters:EmailConverter',
    'uuid': 'vank.core.routing.converters:UUIDConverter',
    'path': 'vank.core.routing.converters:PathConverter',
    'str': 'vank.core.routing.converters:StrConverter',
}
```
详情请看[路由](route.md)
***
### MIDDLEWARES(中间件)

默认值:

```python
[
    'vank.middleware.session.SessionMiddleware'
]
```

中间件能够影响一次请求全局的输入与输出。在这里你可以通过配置模块路径来让vank启动时加载他们,详情请看[中间件](middleware.md)
***
### ERROR_CONVERTER(异常转换器)

默认值: **'vank.core.handlers.exception:default_exception_converter'**
***
### STATIC(静态资源)
***
#### USE_STATIC(是否启用静态文件处理)
默认值: **True**  
是否启用静态文件处理
***
#### STATIC_URL(静态资源URL)
默认值: **'/static/'**  
配置静态资源的路由前缀地址
***
#### STATIC_PATH(静态资源所在目录)
默认值: **PROJECT_DIR / 'statics'**  
你可以通过该配置设定vank在哪里寻找静态资源
***
#### STATIC_ENDPOINT(静态路由端点)
默认值: **'static'**  
静态路由端点
***
### HOT_RELOADER(热重载)
热重载在开发时是一个非常方便快捷的机制,你可以在修改代码后
无需手动重启程序就可以得到反馈,详情请看[热重载](reloader.md)
***
#### AUTO_RELOAD(是否开启热重载)

默认值: **True**  
设置是否使用热重载
***
#### AUTO_RELOAD_INTERVAL(监测间隙)

默认值: **1(单位:s)**  
热重载是通过监测文件的[st_mtime](https://docs.python.org/zh-cn/3/library/os.html#os.stat_result.st_mtime)
来判断项目中的文件对比上一次监测时记录的修改时间是否有变化,而`AUTO_RELOAD_INTERVAL`是配置其监测的间隙
***
### DEFAULT_HOST(主机地址)

默认值: **'127.0.0.1'**  
默认主机地址
***
### DEFAULT_PORT(端口号)

默认值: **5000**  
默认端口号
***
### DEFAULT_CHARSET(编码)

默认值: **'utf-8'**  
默认编码
***
### SESSION(会话)

只有当中间件配置了会话中间件时,以下配置才有效  
在vank中,Session是通过Cookie实现的,所以你应该去了解设置Cookie的[规则](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Set-Cookie)
***
#### SESSION_COOKIE_NAME

默认值: **'sessionid'**  
cookie名字不能包含以下分隔字符：`( ) < > @ , ; : \ " / [ ] ? = { }`
***
#### SESSION_COOKIE_PATH

默认值: **'/'**  
它指定一个 URL 路径，这个路径必须出现在要请求的资源的路径中才可以发送 Cookie 标头
***
#### SESSION_COOKIE_MAX_AGE

默认值: **60 * 60 * 24 * 7**  
在 cookie 失效之前需要经过的秒数。秒数为 0 或 -1 将会使 cookie 直接过期。
假如 `SESSION_COOKIE_EXPIRES` 和 `SESSION_COOKIE_MAX_AGE` 属性均存在，
那么 `SESSION_COOKIE_MAX_AGE` 的优先级更高。
***
#### SESSION_COOKIE_EXPIRES

默认值: **60 * 60 * 24 * 7**  
cookie 的最长有效时间，形式为符合 HTTP-date 规范的时间戳。
***
#### SESSION_COOKIE_HTTP_ONLY

默认值: **False**  
用于阻止JavaScript访问cookie
***
#### SESSION_COOKIE_SAME_SITE

默认值: **'lax'**  
允许服务器设定一则 cookie 不随着跨站请求一起发送,可以有以下值 `strict`、`lax`、`none`
***
#### SESSION_COOKIE_SECURE

默认值: **False**  
使得cookie仅在使用https协议时才会被发送,以阻止`中间人攻击`
***
#### SESSION_COOKIE_DOMAIN

默认值: **None**  
指定 cookie 可以送达的主机名。  
假如没有指定，那么默认值为当前文档访问地址中的主机部分（但是不包含子域名）。
***
### CORS(跨源资源共享)

跨源资源共享（CORS，或通俗地译为跨域资源共享）是一种基于 HTTP 头的机制，该机制通过允许服务器标示除了它自己以外的其它源（域、协议或端口），使得浏览器允许这些源访问加载自己的资源。
跨源资源共享还通过一种机制来检查服务器是否会允许要发送的真实请求，该机制通过浏览器发起一个到服务器托管的跨源资源的“预检(OPTIONS)”请求。
在预检中，浏览器发送的头中标示有 HTTP 方法和真实请求中会用到的头。
详情请看[跨源资源共享](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/CORS)。
***
#### CORS_MAX_AGE

默认值: **500(单位:s)**

指定了OPTIONS请求的结果能被缓存多久,在缓存期间不会再次发送预检请求。
***
#### WITH_CREDENTIALS

默认值: **True**  
告知浏览器是否可以将对请求的响应暴露给前端 JavaScript 代码。
***
#### CORS_ALLOWED_ORIGINS

默认值: **["*"]**  
告诉浏览器哪些源允许访问资源。
或者，对于不需要携带身份凭证的请求，那么可以设置`["*"]`，表示允许来自任意源的请求
***
#### CORS_ALLOWED_METHODS

默认值: **["*"]**  
明确实际的请求所允许的HTTP请求方法。
***
#### CORS_ALLOWED_HEADERS

默认值: **["*"]**  
明确实际的HTTP请求中允许携带的请求头字段。
***

## 指定配置路径
假定你的文件结构如下:
```text
.
├── main.py # 运行服务
└── settings.py # 配置

1 directory, 2 files
```
***
现在如果你想将配置文件移动到configs目录下:
```text
.
├── configs
│       ├── __init__.py
│       └── settings.py # 配置
└── main.py # 运行服务

2 directories, 3 files
```
***
你可以在根目录创建一个名为`run`的python文件,并在里边提前添加配置的路径环境变量。
???+ "run.py"
    ```python
    import os #os模块
    
    os.environ.set_default('PROJECT_SETTING','configs.settings')

    def get_app():
        from main import app #你创建的应用
        return app
    
    if __name__ == '__main__':
        app = get_app()
        app.start()
    ```
最终你的文件结构就像下面一样:
```text
.
├── configs
│       ├── __init__.py
│       └── settings.py # 配置
├── run.py # 运行服务
└── main.py # 创建app

```
