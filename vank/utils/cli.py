# @FileName: cli.py
# @Date    : 2023/1/24-22:25
# @Author  : vank
# @Project : vank
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
        raise NotImplementedError('The run method should be overridden by subclasses')

    def init_arguments(self):
        pass
