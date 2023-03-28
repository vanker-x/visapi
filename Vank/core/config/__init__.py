import os
from importlib import import_module
from Vank.utils.signal import configs_check
from Vank.core.config import base

for item in dir(base):
    if not item.startswith('check_'):
        continue
    f = getattr(base, item)
    if not callable(f):
        continue
    configs_check.bind(getattr(base, item))


class Settings(base.BaseSettings):
    def __init__(self):
        module = os.environ.get('PROJECT_SETTING', None)
        try:
            self.module = import_module(module)
        except:
            raise ModuleNotFoundError(
                f"\n运行失败,未能找到配置模块的路径环境变量(PROJECT_SETTING)\n"
                f"当前配置路径:PROJECT_SETTING='{module}'\n"
                f"请像下面这样添加配置模块的路径:\n"
                f"import os\n"
                f"os.environ['PROJECT_SETTING']='your setting module path'"
            )
        for setting_name in dir(self.module):
            if not setting_name.isupper():
                continue
            setattr(self, setting_name, getattr(self.module, setting_name))
        # 检查配置
        configs_check.emit(self)


conf = Settings()
