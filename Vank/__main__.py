# @FileName: __main__.py
# @Date    : 2023/1/24-21:27
# @Author  : Vank
# @Project : Vank
import sys
import pkgutil
from pathlib import Path
from difflib import get_close_matches
from Vank.utils.cmd import BaseCommand
from Vank.utils.load_module import import_from_str


class MainCommand(BaseCommand):
    epilog = '可以通过 python -m Vank <命令> -h 查看用法'

    def run(self, argv):
        c = argv[1] if len(argv) > 1 else 'help'

        if c in ['help', '-h', '-help']:
            self.print_help()
            sys.exit()
        self.dispatch(c, argv)

    def dispatch(self, c, argv):
        commands = self.find_commands()
        try:
            command_class = commands[c]
        except KeyError:
            self.stderr.write(f'未知命令:{c}\n')
            close_matches = get_close_matches(c, commands)
            if close_matches:
                self.stderr.write(f'与{c}相似的命令有:\n- ')
                self.stderr.write("\n- ".join(close_matches))
        else:
            command_class().run(argv)

    def find_commands(self):
        cmds = {}
        builtin_cmds_path = Path(__file__).parent.joinpath('cli').as_posix()
        for module_finder, name, is_package in pkgutil.iter_modules([builtin_cmds_path]):
            if is_package:
                continue
            cmds.update(
                {name: import_from_str(f'Vank.cli.{name}.Command')}
            )

        return cmds

    def print_help(self):
        self.stdout.write('当前可用的命令有:\n- ')
        self.stdout.write(
            '\n- '.join(
                [
                    f'{name.ljust(25, " ")}{cls.description or "---"}'
                    for name, cls in self.find_commands().items()
                ]
            ))
        self.stdout.write(f'\n\n{self.epilog}')


def entry_point():
    """
    此函数主要作用是为了在分发包时的console_scripts提供入口点
    """
    main = MainCommand()
    sys.exit(main.run(sys.argv))


if __name__ == '__main__':
    entry_point()
