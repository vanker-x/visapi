# Created by vank
# DateTime: 2022/12/7-10:44
# Encoding: UTF-8
import sys
import time
import os.path
import threading
import typing as t
import subprocess
from logging import getLogger
from pathlib import Path

logger = getLogger('console')


class Reloader:
    def __init__(self, interval=1, ):
        self.interval = interval
        self.modify_times = {}

    def run(self):
        while True:
            self.run_tick()
            time.sleep(self.interval)

    def run_tick(self):
        for name in self.get_stat_paths():
            current_modify_time = os.stat(name).st_mtime
            previous_modify_time = self.modify_times.get(name, None)
            if not previous_modify_time:
                self.modify_times[name] = current_modify_time
                continue

            if current_modify_time > previous_modify_time:
                logger.warning(f'File {name} has changed!')
                self.trigger_reload()

    def trigger_reload(self):
        sys.exit(3)

    def restart_with_reloader(self):
        """
        通过subprocess重启服务
        """
        while 1:
            logger.warning('The service has changed and is currently restarting'.center(20, '='))
            # 获取启动参数
            args = self._get_args_for_reloading()
            # 创建新的环境变量
            environment = {**os.environ.copy(), 'autoreload': '1'}
            # 启动新的子进程服务、在重载的服务未退出时会阻塞
            exit_code = subprocess.call(args, env=environment)
            # 判断exit_code是否为3，否则结束当前服务
            if not exit_code == 3:
                return exit_code

    def get_stat_paths(self):
        for director in [Path(os.getcwd())]:
            for file in director.rglob('*.py'):
                yield file.resolve()

    def _get_args_for_reloading(self) -> t.List[str]:
        """
        获取服务的启动方式
        """
        entry_point, *args = sys.argv
        # 判断是否为windows,并且是以可执行文件的方式开启服务的.
        if os.name == 'nt' and entry_point.endswith('.exe'):
            res = [entry_point]
        else:
            res = [sys.executable, entry_point]
        res += args
        return res


def run_in_reloader(target_func, interval):
    try:
        reloader = Reloader(interval)
        # 由reloader重启服务
        if os.environ.get('autoreload', None):
            # main_func会在reloader主线程关闭时关闭
            main_func = threading.Thread(target=target_func)
            main_func.daemon = True
            main_func.start()
            reloader.run()
        else:
            # 第一次启动服务
            sys.exit(reloader.restart_with_reloader())
    except KeyboardInterrupt:
        pass
