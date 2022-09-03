# Created by Vank
# DateTime: 2022/8/22-11:44
# Encoding: UTF-8
import os
import sys
from create_project import Process as create_project_process


def main(*commands):
    if len(commands) < 2:
        print(f'至少包含两个变量 实际收到{len(commands)}个')
        return
    if commands[0] == 'createproject':
        project_name = commands[1]
        create_project_process(project_name).start()
        return


if __name__ == '__main__':
    args = sys.argv[1:]
    main(*args)

