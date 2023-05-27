# @FileName: cli.py
# @Date    : 2023/1/24-22:25
# @Author  : Vank
# @Project : Vank
import sys
from argparse import ArgumentParser


class BaseCommand:
    description = None
    usage = None
    epilog = None

    def __init__(self):
        self.stderr = sys.stderr
        self.stdout = sys.stdout
        self.parser = ArgumentParser(
            description=self.description,
            usage=self.usage,
            epilog=self.epilog
        )
        self.init_arguments()

    def run(self, argv):
        raise NotImplementedError('run方法应该由子类重写')

    def init_arguments(self):
        pass
