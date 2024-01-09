# 中间件
中间件是贯穿整个请求的钩子,它可以在一次请求之前或者返回响应之前进行工作:  
- handle_request: 在请求到来时工作(请求这时还没有进行路由匹配)  
- handle_view:在请求进入视图时工作(请求已经进行路由匹配,并且找到了对应的视图。但还未进入视图).  
- handle_response:在视图返回响应之后工作(已经交由视图处理,并且视图返回了响应).  
***
## 自定义中间件
### 创建中间件
创建一个自定义的中间件你可以像下面这样:
```python title="my_middleware.py"
from vank.middleware.base import BaseMiddleware

class MyMiddleware(BaseMiddleware):
    def handle_request(self,request):
        pass
    
    def handle_view(self,request,view_func,**view_kwargs):
        pass
    
    def handle_response(self,request,response):
        pass
```
假设你需要计算本次请求消耗的时间,你可以在handle_request和handle_response方法中这样写:
```python title="my_middleware.py"
from vank.middleware.base import BaseMiddleware
from time import time

class MyMiddleware(BaseMiddleware):
    def handle_request(self,request):
        time_start = time() #获取开始时间
        setattr(request,"time_start",time_start) #设置start_time属性
        return None

    def handle_view(self,request,view_func,**view_kwargs):
        pass
    
    def handle_response(self,request,response):
        end_time = time() #获取结束时间
        print(f'本次请求共花费:{end_time-request.start_time}s')
        return response
```
***
### 添加到设置
在创建完自定义的中间件之后,你可以将它添加到你的`settings.py`([配置](settings.md#middlewares))中
```python title="settings.py"
MIDDLEWARES = [
...
'my_middleware.MyMiddleware'
]
```

!!! warning "注意"
    配置中间件的顺序非常重要,配置顺序越靠前,那么中间件的handle_request和handle_view越早被执行,
    而handle_response相反。  
<figure markdown>
  ![图片](../../images/middleware.png#only-light){ loading=lazy }
  ![图片](../../images/middleware_dark.png#only-dark){ loading=lazy }
  <figcaption>中间件工作流程</figcaption>
</figure>
