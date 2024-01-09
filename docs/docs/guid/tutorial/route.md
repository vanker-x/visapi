# 路由

在后端项目中,规划一个简洁明了的URL是非常重要的,这里将教你如何创建一个URL与回调函数([视图](view.md))的映射
当请求到来时,vank会根据请求的路径依次遍历(其顺序取决于你注册路由的顺序)当前应用中所有的路由规则。

如果有路由规则与请求路径相匹配,那么将会提取路径中有用的数据(取决于你在注册路由时设置了路由转换器)。
***
## 注册路由

在创建应用后,你可以通过应用的`new_route`方法来将一个视图注册到你的服务中:

```python
from vank.core import Application, request, response

app = Application()

@app.new_route('/')
def index( *args, **kwargs):
    return response.ResponsePlain('this is route tutorial')
```
***
## 路径参数
你可以通过在注册路由时为路径设置一个路由转换器,告诉路由系统这条路径有参数需要被提取:
```python hl_lines="5-8"
from vank.core import Application, request, response

app = Application()

@app.new_route('/{_id:int}')
def index(_id, *args, **kwargs):
    print(f'id是:{_id}')
    return response.ResponsePlain(f'id是:{_id}')

```
`{_id:int}`指的是提取/后面的int类型的数据,并且以`_id`传入到中
当你请求[http://127.0.0.1:5000/1](http://127.0.0.1:5000/1)时,在你的视图中`print(_id)`会显示`id是:1`。  
所以你的视图必须设置一个名为_id的形参或者使用**kwargs(可变位置参数)来接收他。
***
## 路由转换器
vank为你提供了一些内置的路由转换器你可以在`settings.py`([配置](settings.md#route_converters))看到他们:
```python title="settings.py"
...
# 含参数路由转换器
ROUTE_CONVERTERS = {
    'int': 'vank.core.routing.converters:IntConverter',
    'float': 'vank.core.routing.converters:FloatConverter',
    'email': 'vank.core.routing.converters:EmailConverter',
    'uuid': 'vank.core.routing.converters:UUIDConverter',
    'path': 'vank.core.routing.converters:PathConverter',
    'str': 'vank.core.routing.converters:StrConverter',
}
```
`ROUTE_CONVERTERS`是一个字典,拿`'int': 'vank.core.routing.converters:IntConverter'`来举例,
`int`指的是这个转换器的名字,后面的字符串是这个转换器的引用路径。  
这样,在你启动服务时,vank就会帮你加载这些转换器
***
## 自定义路由转换器
### 创建路由转换器
除了vank提供的内置路由转换器,你也可以自定义一个路由转换器:
```python title="my_converters.py"
from vank.core.routing.converters import BasicConverter

class MyConverter(BasicConverter):
    regex = '\d{2,3}'
    name = 'limited_int'

def convert_to_python(self,value):
    return int(value)

def convert_to_url(self,value):
    return str(value)

```
其中有两个类属性,`regex`会在构正则路由时使用,`name`代表这个转换器的名字  
还有两个抽象方法(abstract method),`convert_to_python`会在请求到来提取参数时用到,`convert_to_url`与之对立.
所以你必须实现这两个方法  
***
### 添加到设置
在`settings.py`([配置](settings.md#route_converters))加入你自定义的转换器(假定`my_converters.py`与`settings.py`同级目录):
```python title="settings.py" hl_lines="10"
...
# 含参数路由转换器
ROUTE_CONVERTERS = {
    'int': 'vank.core.routing.converters:IntConverter',
    'float': 'vank.core.routing.converters:FloatConverter',
    'email': 'vank.core.routing.converters:EmailConverter',
    'uuid': 'vank.core.routing.converters:UUIDConverter',
    'path': 'vank.core.routing.converters:PathConverter',
    'str': 'vank.core.routing.converters:StrConverter',
    'limited_int':'my_converters:Myconverter'
}
```
***
### 使用路由转换器
接下来你就可以在注册路由时使用你的路由转换器了
```python title="views.py" hl_lines="5"
from vank.core import Application, request, response

app = Application()

@app.new_route('/{_id:limited_int}')
def index(_id, *args, **kwargs):
    return response.ResponsePlain(f'限制长度后的int类型:{_id}')
```
访问 [http://127.0.0.1:5000/123](http://127.0.0.1:5000/123),是可以提取到`123`的  
但是如果访问[http://127.0.0.1:5000/1](http://127.0.0.1:5000/123)则会提示404错误.