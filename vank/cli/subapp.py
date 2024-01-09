# @FileName: subapp.py
# @Date    : 2023/1/27-1:29
# @Author  : vank
# @Project : vank
import os
import sys

from vank.utils.cli import BaseCommand

try:
    import pydantic
except Exception as e:
    HAVE_PYDANTIC = False
else:
    HAVE_PYDANTIC = True

control_template = """"""
views_template = """
from vank.core import SubApplication, request, response

{name}_sub = SubApplication('{name}')

# Type your view code here

"""
init_template = """"""
schema_template = """
from pydantic import BaseModel

# Type your schema code here

"""
subapp_files = {
    'control.py': control_template,
    'views.py': views_template,
    '__init__.py': init_template
}
if HAVE_PYDANTIC:
    subapp_files["schema.py"] = schema_template


class Command(BaseCommand):
    description = 'You can create a sub application through this command'

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
            self.stderr.write(f'The "{name}" sub application already exists and cannot be created\n')
            sys.exit()
        for file_name, template in subapp_files.items():
            with open(os.path.join(sub_app_dir, file_name), 'w', encoding='utf-8') as f:
                f.write(template.lstrip().format(name=name))

    def init_arguments(self):
        self.parser.add_argument(
            '-n',
            '--name',
            help='Name of sub application',
            required=True
        )
        self.parser.add_argument(
            '-d',
            '--directory',
            help='Specify the directory where the sub application is located'
        )
