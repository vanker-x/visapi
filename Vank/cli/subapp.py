# @FileName: subapp.py
# @Date    : 2023/1/27-1:29
# @Author  : Vank
# @Project : Vank
import os
import sys

from Vank.utils.cli import BaseCommand

control_template = """"""
views_template = """
from Vank.core.app import SubApplication

{name}_sub = SubApplication('{name}')

# 在此编码

"""
init_template = """"""
subapp_files = {
    'control.py': control_template,
    'views.py': views_template,
    '__init__.py': init_template
}


class Command(BaseCommand):
    description = '你可以通过此命令创建一个子应用'

    def run(self, argv):
        options, args = self.parser.parse_known_args(argv[2:])
        name = options.name
        dir_ = options.directory
        if not dir_:
            sub_app_dir = os.path.join(os.getcwd(), name)
        else:
            sub_app_dir = os.path.join(dir_, name)
        try:
            os.makedirs(sub_app_dir)
        except FileExistsError:
            self.stderr.write(f'"{name}"子应用已存在,无法创建')
            sys.exit()
        for file_name, template in subapp_files.items():
            with open(os.path.join(sub_app_dir, file_name), 'w', encoding='utf-8') as f:
                f.write(template.lstrip().format(name=name))

    def init_arguments(self):
        self.parser.add_argument(
            '-n',
            '--name',
            help='子应用的名称',
            required=True
        )
        self.parser.add_argument(
            '-d',
            '--directory',
            help='指定子应用所在的目录'
        )
