# 子应用

子应用是为了增强应用的灵活性以及实现模块化而设计的,并且不同的子应用下可以创建相同的视图名称。
这里我们可以把`Application`作为主应用,而子应用具有和主应用大致相同的功能,例如`new_route`、`get`、`post`等注册路由的方法;
主应用可以通过`include`方法挂载多个子应用:
<figure markdown>
  ![图片](../../images/application.png#only-light){ loading=lazy }
  ![图片](../../images/application_dark.png#only-dark){ loading=lazy }
  <figcaption>子应用</figcaption>
</figure>

***

## 创建一个子应用

`vank`为你提供了创建子应用的快捷方式(命令行工具):
首先当前的目录结构为:
```text
.
├── main.py
└── settings.py

1 directory, 2 files

```
运行创建子应用命令
```shell
> vank subapp  -n my_app -d apps
```

- `-n` (必填)为子应用指定名称
- `-d` (选填)为子应用指定所在位置  
***
运行完命令之后你将会得到下面这样的文件结构:
```text
.
├── apps
│   └── api
│       ├── __init__.py
│       ├── control.py
│       └── views.py
├── main.py
└── settings.py

3 directories, 5 files

```
***
## 编写子应用视图
```python title="views.py"
from vank.core import SubApplication, request, response

api_sub = SubApplication('api')

@api_sub.get('/')
def sub_index():
    return response.ResponsePlain("这是api子应用的index视图")
```
## 注册子应用
=== "通过主应用的include方法1"
    ```python
    from apps.api.view import api_sub
    ...
    app.include(api_sub)
    ```
=== "通过主应用的include方法2"
    ```python
    ...
    app.include("apps.api.views:api_sub")
    ```
=== "在设置中配置子应用实例路径(推荐)"
    ```python
    SUB_APPLICATIONS = [
    ...
    "apps.api.views:api_sub"
    ]

    ```