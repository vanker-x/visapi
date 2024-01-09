# 一些建议

## 视图与逻辑分离

通常我们的逻辑是写在视图中的,就像这样

```python title="views.py"
...


@app.get('/')
def foo(*args, **kwargs):
    data = request.param
    foo_id = data['id']
    foo_name = data['name']
    ...
    # 做一些查询操作
```

这样给我们带来的一个问题是,如果我只是想要验证我的数据库查询操作是否正确,我不得不需要启动服务才能验证,所以我们应该将逻辑代码与视图分离开。
在子应用文件夹下创建名为`control.py`的python文件
并在其中编写代码,如:

```python title="control.py"
def foo_get(foo_id, foo_name):
    ...
    # 做一些查询操作
    return something
```

在views引入control模块

```python title="views.py"
...
from apps.foo_app import control as ct


@app.get('/')
def foo( *args, **kwargs):
    data = request.param
    foo_id = data['id']
    foo_name = data['name']
    res = ct.foo_get(foo_id, foo_name)
```

如果需要验证我们的查询操作是否正确则可以创建一个名为`control_test.py`的python文件,并编写代码:

```python title="control_test.py"
from apps.foo_app import control as ct


def test_foo_get():
    foo_id = 1
    foo_name = 'bar'
    res = ct.foo_get(foo_id, foo_name)
    print(res)


if __name__ == '__main__':
    test_foo_get()

```

**注意传入foo_get函数的参数类型应尽量为基础的python类型**

## 数据校验

推荐使用python数据校验库[pydantic](https://docs.pydantic.dev/)
你可以在子应用文件夹下创建名为`schema.py`的python文件
并在其中编写数据校验代码,如:

```python title="schema.py"
import typing as t
from pydantic import BaseModel, validator


class IndexGetSchema(BaseModel):
    foo: int
    bar: int

```

在views中引入数据校验模块

```python title="views.py"
...
from apps.foo_app import schema as sc

...
```

在视图函数中使用数据校验

```python title="views.py"
...


@app.get('/')
def index(*args, **kwargs):
    data = sc.IndexSchema(**request.param)
    print(data.foo)
    print(data.bar)
```

**值得注意的是使用pydantic校验数据可能会引发错误,这些错误应该由我们正确的处理**
