# 使用SQLAlchemy

在`vank`中使用[SQLAlchemy](https://www.sqlalchemy.org/)和中间件和配置有关,如果你对他们不了解,请先了解[中间件](middleware.md)和[配置](settings.md)

## 下载SQLAlchemy
```shell
> pip install sqlalchemy
```
***
## 声明模型
```python title="db/models.py"
from sqlalchemy import schema as sc
from sqlalchemy import types as fields
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    ...


class User(Base):
    __tablename__ = "user"
    id = sc.Column(fields.Integer, primary_key=True, doc="id")
    username = sc.Column(fields.String(30), unique=True, doc="username")
    password = sc.Column(fields.String(200), doc="password")

```
***
## 创建连接引擎并创建表
```python title="db/engine.py"
from db.models import Base
from sqlalchemy import create_engine

engine = create_engine("sqlite://", echo=True)

if __name__ == '__main__':
    Base.metadata.create_all(engine)
```
`echo=True`参数表示连接提交的SQL将被记录到标准输出。

`create_all`方法将会发起创建表的DDL(没错,就是你想的DDL和DML的那个DDL)指令
***
## 创建session
```python title="db/initialize.py"
from db.engine import engine
from sqlalchemy.orm import sessionmaker, scoped_session

Session = sessionmaker(engine)
session = scoped_session(Session)

```
***
## 创建SQLAlchemy中间件
```python title="db/middlewares.py"
from db.initialize import session
from vank.middleware.base import BaseMiddleware

class SQLAlchemyMiddleware(BaseMiddleware):
    def handle_response(self,response):
        session.remove()
        return response
```
***
## 将middleware添加至[设置](settings.md#middlewares)中

```python title="settings.py"
...
MIDDLEWARES=[
    ...
    "db.middlewares:SQLAlchemyMiddleware"
]
```
值得注意的是需要确保在session被remove后，后面的中间件不会使用该session；所以**建议将该中间件放到MIDDLEWARES列表最末尾**
## 创建用户对象并持久化
```python title="xxx.view.py"
from db.models import User
from db.initialize import session
...

@app.post('/api/user')
def create_user_view(*args, **kwargs):
    user = User(username="hello", password="vank")
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    ...

```