# @filename: __init__.py.py
# @Time:    2022/7/26-2:31
# @Author:  Vank


def setup_config():
    """
    设置项目配置到环境变量中 以便框架能够读取到项目的settings.py 文件
    :return:
    """
    import os
    import sys
    from pathlib import Path
    if os.environ.get('PROJECT_SETTING'):
        return
    main_file = sys.argv[0]
    project_name = Path(main_file).parent.name
    os.environ.setdefault('PROJECT_SETTING', f'{project_name}.settings')


setup_config()
from Vank.core.app import Application, SubApplication
