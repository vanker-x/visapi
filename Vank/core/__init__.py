# @filename: __init__.py.py
# @Time:    2022/7/26-2:31
# @Author:  Vank

def app(file):
    import os
    from pathlib import Path
    Project_Dir = Path(file).parent.name
    os.environ.setdefault('PROJECT_SETTING', f'{Project_Dir}.settings')
    from .app import App
    return App()
