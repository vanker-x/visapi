# Created by Vank
# DateTime: 2022/12/7-10:44
# Encoding: UTF-8
import sys
import time
import os.path
import threading
import typing as t
import subprocess
from functools import partial
from logging import getLogger
from pathlib import Path

logger = getLogger()
default_file_suffix = {'.py', '.pyc', '.html', '.vue', '.js', '.js'}


class Reloader:
    def __init__(self,
                 interval=1,
                 spec_file_suffixes: t.Optional[t.Iterable[str]] = None,
                 exclude_file_suffixes: t.Optional[t.Iterable[str]] = None,
                 ):
        self.interval = interval
        self.modify_times = {}
        # 默认文件后缀并上指定文件后缀
        suffix = default_file_suffix.union(spec_file_suffixes or {})
        # 减去需要排除的后缀
        self.file_suffixes = tuple(suffix.difference(exclude_file_suffixes or {}))

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
                logger.warning(f'检测到文件{name}已经改变 重启!')
                self.trigger_reload()

    def trigger_reload(self):
        sys.exit(3)

    def restart_with_reloader(self):
        while 1:
            logger.warning('通过重载器重新加载'.center(20, '='))
            # 获取启动参数
            # args = [sys.executable, '-m', 'main']
            args = self._get_args_for_reloading()
            # 创建新的环境变量
            environment = {**os.environ.copy(), 'autoreload': '1'}
            exit_code = subprocess.call(args, env=environment)
            if not exit_code == 3:
                return exit_code

    def get_stat_paths(self):
        for director in [Path(os.getcwd())]:
            for file in director.rglob('*.py'):
                yield file.resolve()
        #
        # paths = set()
        # for path in sys.path:
        #     path = os.path.abspath(path)
        #     if os.path.isfile(path) and path.endswith(self.file_suffixes):
        #         paths.add(path)
        #         continue
        #
        #     for root, dir_, files in os.walk(path):
        #         path_join = partial(os.path.join, root)
        #         if os.path.basename(root) in ['__pycache__']:
        #             continue
        #
        #         exist_python_file = False
        #         for name in files:
        #             if name.endswith(self.file_suffixes):
        #                 exist_python_file = True
        #                 paths.add(path_join(name))
        #         if not exist_python_file:
        #             continue
        # return paths

    def _get_args_for_reloading(self) -> t.List[str]:
        """Determine how the script was executed, and return the args needed
        to execute it again in a new process.
        """
        rv = [sys.executable]
        py_script = sys.argv[0]
        args = sys.argv[1:]
        # Need to look at main module to determine how it was executed.
        __main__ = sys.modules["__main__"]

        # The value of __package__ indicates how Python was called. It may
        # not exist if a setuptools script is installed as an egg. It may be
        # set incorrectly for entry points created with pip on Windows.
        if getattr(__main__, "__package__", None) is None or (
                os.name == "nt"
                and __main__.__package__ == ""
                and not os.path.exists(py_script)
                and os.path.exists(f"{py_script}.exe")
        ):
            # Executed a file, like "python app.py".
            py_script = os.path.abspath(py_script)

            if os.name == "nt":
                # Windows entry points have ".exe" extension and should be
                # called directly.
                if not os.path.exists(py_script) and os.path.exists(f"{py_script}.exe"):
                    py_script += ".exe"

                if (
                        os.path.splitext(sys.executable)[1] == ".exe"
                        and os.path.splitext(py_script)[1] == ".exe"
                ):
                    rv.pop(0)

            rv.append(py_script)
        else:
            # Executed a module, like "python -m werkzeug.serving".
            if os.path.isfile(py_script):
                # Rewritten by Python from "-m script" to "/path/to/script.py".
                py_module = t.cast(str, __main__.__package__)
                name = os.path.splitext(os.path.basename(py_script))[0]

                if name != "__main__":
                    py_module += f".{name}"
            else:
                # Incorrectly rewritten by pydevd debugger from "-m script" to "script".
                py_module = py_script

            rv.extend(("-m", py_module.lstrip(".")))

        rv.extend(args)
        return rv


def run_in_reloader(target_func, interval, spec_file_suffix, ignore_file_suffix):
    try:
        reloader = Reloader(interval, spec_file_suffix, ignore_file_suffix)
        if os.environ.get('autoreload', None):
            main_func = threading.Thread(target=target_func)
            main_func.daemon = True
            main_func.start()
            reloader.run()
        else:
            sys.exit(reloader.restart_with_reloader())
    except KeyboardInterrupt:
        pass
