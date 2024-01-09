# 创建应用

## 命令行功能
你可以通过在命令行输入`vank`查看vank提供了哪些命令行功能:
```shell 
> vank
The currently available commands are:
- init                     Initialize the project through this command
- subapp                   You can create a sub application through this command

You can view usage through python -m vank <command> -h
```
现在,你可以看到`init`命令可以初始化你的项目,你可以通过`vank init -h`查看它的具体用法
```shell
> vank init -h
usage: vank [-h] [-n NAME]

Initialize the project through this command

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Initialize the project in a new directory
```
可以看到你可以通过`-n`为项目指定名称,但这是一个可选参数  
=== "当前文件夹下初始化"
    ```shell
    > vank init
    ```
=== "指定项目名称"
    ```shell
    > vank init -n mysite
    ```
***
## 初始化应用
接着[安装](../installation.md)的步骤你可以在当前文件夹下运行第一种方法`vank init`  
这样就会得到以下两个文件
```text
.
├── main.py
└── settings.py

1 directory, 2 files

```
???+ "settings.py"
    ```python
    from pathlib import Path
    
    PROJECT_BASE_DIR = Path(__file__).parent
    # 密钥
    SECRET_KEY = '61d38a9932f59aa4adec525e77d6c37a19b38390b7427ce924651213296c751e'
    
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
    
    # 异常转换器
    ERROR_CONVERTER = 'vank.core.handlers.exception:default_exception_converter'
    
    # 处理静态文件(生产环境请设置为False)
    USE_STATIC = True
    
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
    

    ```
???+ "main.py"
    ```python
    from vank.core import Application, request, response
    
    app = Application()
    
    
    @app.new_route('/')
    def say_hi(*args, **kwargs):
        return response.ResponsePlain(f'Hi,your request path is {request.path}')
    
    
    if __name__ == '__main__':
        app.start()
    ```
***
## 运行服务
通过终端运行服务
```shell
> python main.py

The service has changed and is currently restarting
Your service is running on:http://127.0.0.1:5000/
- Do not use in production environment
- Version number:1.0.3
```
***
## 步骤讲解
### 1.从vank的核心导入Application
Application这个类提供了一系列的方法来快速的创建一个web应用
```python title="main.py" hl_lines="1"
from vank.core import Application, request, response

app = Application()


@app.new_route('/')
def say_hi(*args, **kwargs):
    return response.ResponsePlain(f'Hi,your request path is {request.path}')


if __name__ == '__main__':
    app.start()
```
***
### 2.创建一个应用
实例化Application类可以得到一个遵循[WSGI](https://peps.python.org/pep-3333/)(Python Web Service Gateway Interface)规范的实例;如果想要了解Python Web框架的实现原理,这里强烈建议去看一下WSGI规范
```python title="main.py" hl_lines="3"
from vank.core import Application, request, response

app = Application()


@app.new_route('/')
def say_hi(*args, **kwargs):
    return response.ResponsePlain(f'Hi,your request path is {request.path}')


if __name__ == '__main__':
    app.start()
```
***
### 3.创建一条路由规则
创建路由规则指的是URL以/开始以后的部分,与对应这条规则的回调函数进行绑定(**绑定是通过闭包实现的**)就像下面这样:
```python title="main.py" hl_lines="6-8"
from vank.core import Application, request, response

app = Application()


@app.new_route('/')
def say_hi(*args, **kwargs):
    return response.ResponsePlain(f'Hi,your request path is {request.path}')


if __name__ == '__main__':
    app.start()
```
当请求到来时app会根据请求路径对路由注册的先后顺序依次匹配,如果匹配成功那么app会将**request**以及一些从路径中提取的信息交由回调函数(例如上方的say_hi),反之,**如果所有的路由规则都未匹配到则会raise一个404错误**
***
### 4.运行服务
```python title="main.py" hl_lines="11-12"
from vank.core import Application, request, response

app = Application()


@app.new_route('/')
def say_hi(*args, **kwargs):
    return response.ResponsePlain(f'Hi,your request path is {request.path}')


if __name__ == '__main__':
    app.start()
```
app会在本地开启一个实时服务器,服务器主机与端口号取决于`settings.py`中的**DEFAULT_HOST**,**DEFAULT_PORT** 默认主机和端口号为127.0.0.1([环回地址](https://zh.wikipedia.org/wiki/Localhost))、5000
