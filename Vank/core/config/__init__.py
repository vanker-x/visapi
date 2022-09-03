from importlib import import_module
import os

ENVIROMENT_VARIABLE_OF_PROJECT = 'PROJECT_SETTING'


class Settings:
    def __init__(self):
        module = os.environ.get(ENVIROMENT_VARIABLE_OF_PROJECT, '')
        if not module:
            raise RuntimeError(
                "运行失败,运行时未找到settings.py的环境变量 PROJECT_SETTING"
                "你必须先配置settings.py文件的环境变量"
            )
        try:
            self.module = import_module(module)
        except:
            raise RuntimeError('加载设置文件失败,请查看是否设置正确')

    def __getattr__(self, item):
        value = getattr(self.module, item, None)
        if not value:
            raise AttributeError(f'没有找到属性:{item}')
        self.__dict__[item] = value

        return value


conf = Settings()
