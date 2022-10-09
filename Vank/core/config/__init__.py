import os
from importlib import import_module

from Vank.core.config.base import BaseSettings

ENVIROMENT_VARIABLE_OF_PROJECT = 'PROJECT_SETTING'


class Settings(BaseSettings):
    def __init__(self):
        module = os.environ.get(ENVIROMENT_VARIABLE_OF_PROJECT, None)
        if not module:
            raise ModuleNotFoundError(
                "运行失败,运行时未找到settings.py的环境变量 PROJECT_SETTING"
                "你必须先配置settings.py文件的环境变量"
            )
        try:
            self.module = import_module(module)
        except:
            raise ModuleNotFoundError('加载settings失败,你把项目中的settings.py删除了吗?')
        for setting_name in dir(self.module):
            if not setting_name.isupper():
                continue
            setattr(self, setting_name, getattr(self.module, setting_name))


conf = Settings()
