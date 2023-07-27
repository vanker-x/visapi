import os
from importlib import import_module
from vank.utils.signal import configs_check
from vank.core.config import base

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
                f"\nFailed, unable to find path environment variable for configuration module (PROJECT SETTING)\n"
                f"Current configuration module path:PROJECT_SETTING='{module!r}'\n"
                f"Please add the correct path for the configuration module as follows:\n"
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
