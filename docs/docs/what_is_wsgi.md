# 什么是WSGI?

WSGI([Python Web Server Gateway Interface](https://peps.python.org/pep-3333/))是一个描述Web服务器和Python
Web应用或框架之间通信的规范,它并不是一个具体的软件应用程序。
它解释了Web服务器如何与Python Web应用或框架进行通信,以及如何连接Web应用或框架以处理请求。

#### 名词解释

1. Web服务器:诸如nginx、apache这些能够处理HTTP请求和响应的软件应用。
2. Python Web应用/框架:能够处理用户一系列动态请求的Python应用程序。

***

## 为什么出现WSGI

在没有WSGI之前,选择一个合适的Python Web框架成为困扰初学者的问题。因为选择一个框架往往会限制你
对Web服务器的选择,因为那时框架是针对Web服务器所支持的API所设计的。也就是说你选择的框架并不能随心所欲的更换Web服务器。  
而WSGI就是为了解决这个令人头疼的问题,它提出了一个Web服务器与Python应用或框架之间通用的、低级的接口。
使得开发人员能自由的选择框架和Web服务器,更加专注的研究他们喜欢的领域。
<figure markdown>
  ![图片](images/before_wsgi.png#only-light){ loading=lazy }
  ![图片](images/before_wsgi_dark.png#only-dark){ loading=lazy }
  <figcaption>出现WSGI之前</figcaption>
</figure>
<figure markdown>
  ![图片](images/after_wsgi.png#only-light){ loading=lazy }
  ![图片](images/after_wsgi_dark.png#only-dark){ loading=lazy }
  <figcaption>出现WSGI之后</figcaption>
</figure>
***
## WSGI规格描述
总的来说WSGI规范由三个组件组成:

* WSGI服务器
* WSGI中间件
* Python应用/框架

### WSGI服务器

WSGI服务器是Web服务器和Python应用/框架之间通讯的桥梁。Web服务器与Python应用/框架之间通讯
必须经过WSGI服务器,并由WSGI服务器来整理HTTP请求、HTTP响应。
***

### WSGI中间件
WSGI中间件是指一种可以包装Python应用/框架的组件,它可以拦截HTTP请求和响应,并对它们进行修改或处理。
中间件可以实现各种功能,如身份验证、日志记录等,从而使Python应用/框架更加灵活、可扩展。  
WSGI中间件是按照一定的顺序组合在一起的,每个中间件都会对HTTP请求和响应进行处理,并将处理结果传递给下一个中间件,最终传递给Python应用/框架。  
在处理WSGI服务器传过来的请求时,中间件可以对请求进行修改或拦截,然后将修改后的请求传递给下一个中间件或Python应用/框架。  
在处理Python应用/框架的响应时,中间件也可以对响应进行修改或拦截,然后将修改后的响应传递给上一个中间件或WSGI服务器。
***

### Python应用/框架

Python应用/框架必须为一个可调用对象,它可以是函数、类、方法或者是一个实现了__call__魔术方法的实例对象等。
并且它必须接收两个位置参数:

- environ
- start_response
#### environ
environ是一个包含HTTP请求信息的字典,它包括了HTTP请求的各种信息,如请求方法、路径、查询参数、请求头等。
在WSGI应用程序中,可以通过访问environ对象来获取这些信息,以便处理HTTP请求。
#### start_response
start_response是一个函数,用于发送HTTP响应头。
WSGI应用程序需要在处理完HTTP请求后调用start_response函数来发送HTTP响应头。
start_response函数接受两个参数：status和response_headers。status是一个字符串,表示HTTP响应状态码和原因短语,如"200 OK"。
response_headers是一个包含HTTP响应头信息的列表,每个元素都是一个元组，表示一个HTTP响应头的名称和值,如('Content-Type','text/html')。
***

## 简单实现

Python为我们提供了一个简单的WSGI服务器内置库,名字叫做wsgiref。接下来我们使用它来简单的实现一个服务
***
### 实现服务
```python
from wsgiref.simple_server import make_server  # 导入wsgi服务器


def application(environ, start_response):
    """
    这是一个Python应用
    """
    # 调用start_response
    start_response('200 OK', [('Content-Type', 'text/html')])
    # 返回可迭代二进制字符
    return [b'<h1>Simple~<h1>']


# 创建服务并开启
make_server('0.0.0.0', 5000, application).serve_forever()
```
***
### 通过中间件捕获错误
```python
from functools import wraps
from wsgiref.simple_server import make_server  # 导入wsgi服务器

def middleware(func):
    #这是一个WSGI中间件
    @wraps(func)
    def inner(*args,**kwargs):
        try:
            #调用Python应用或下一个WSGI中间件
            response = func(*args,**kwargs)
        except Exception as e:
            #发生错误,重新生成response
            response = [b'Error']
        return response
    return inner

@middleware
def application(environ, start_response):
    """
    这是一个Python应用
    """
    # 调用start_response
    start_response('200 OK', [('Content-Type', 'text/html')])
    # 返回可迭代二进制字符
    return [b'<h1>Simple~<h1>']


# 创建服务并开启
make_server('0.0.0.0', 5000, application).serve_forever()
```
我们可以通过装饰器的方式,将Python应用包装起来,这样当WSGI服务器调用`application`时,其实真正被调用的是`middleware.inner`,
而inner这个函数对真正的Python应用进行了调用,但是捕获了Python应用里可能出现的错误。
!!! warning "注意"
    这只是关于WSGI的示范,并非vank的开发样例。