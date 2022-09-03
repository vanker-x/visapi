# Created by Vank
# DateTime: 2022/8/22-11:45
# Encoding: UTF-8
import os
import random


class Templates:
    setting_notes = '''"""
这是项目 %s 的设置文件,请勿删除
"""'''

    setting = '''
from pathlib import Path

PROJECT_BASE_DIR = Path(__file__).parent
# 密钥
SECRET_KEY = '%s'

# 数据库配置
DATABASE = {
    'ENGINE': 'peewee.SqliteDatabase',
    'DATABASE_CONFIG': {
        'NAME': PROJECT_BASE_DIR / 'test.db'
    }
}

# 含参数路由转换器
ROUTE_CONVERTERS = {
    'int': 'Vank.core.route.converters.IntConverter',
    'float': 'Vank.core.route.converters.FloatConverter',
    'email': 'Vank.core.route.converters.EmailConverter'
}'''

    demo = '''from Vank.core import App
from Vank.core.http.response import Response

# 创建一个app
app = App(__file__)


# 新增一条路由
@app.new_route('/', ['GET'])
def helloworld(request):
    # 返回一个响应
    return Response(request, 'Hello Vank!')


if __name__ == '__main__':
    # 开启服务
    app.start('127.0.0.1', 8000)'''


class Process:
    def __init__(self, project_name):
        self.pro_name = project_name

    def mkdir(self):
        os.mkdir(self.pro_name)

    def get_random_key(self):
        temp = '123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM<>?!@#$%^&*'
        key = ''
        for i in range(random.randint(50, 80)):
            key += temp[random.randint(0, len(temp) - 1)]
        return key

    def mk_settings(self):
        with open(rf'{self.pro_name}/settings.py', 'w', encoding='utf-8') as f:
            f.write(Templates.setting_notes % (self.pro_name))
            f.write(Templates.setting % self.get_random_key())

    def mk_demo(self):
        with open(f'{self.pro_name}/main.py', 'w', encoding='utf-8') as f:
            f.write(Templates.demo)

    def start(self):
        self.mkdir()
        self.mk_settings()
        self.mk_demo()
        print(f'创建项目 {self.pro_name} 成功')
