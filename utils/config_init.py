import os
import sys

import refconfig
from oba import Obj
from refconfig import RefConfig
from smartdict import DictCompiler

from utils.dynamic_parser import DynamicParser


class PathSearcher(DictCompiler):
    compiler = DictCompiler({})

    @classmethod
    def search(cls, d: dict, path: str):
        cls.compiler.d = d
        cls.compiler.circle = {}
        return cls.compiler._get_value(path)


makedirs = []


def config_init():
    required_args = ['data', 'model', 'exp']

    command = ' '.join(sys.argv[1:])
    args, kwargs = DynamicParser.parse(command)

    for arg in required_args:
        if arg not in kwargs:
            raise ValueError(f'miss argument {arg}')

    config = RefConfig().add(refconfig.CType.SMART, kwargs).parse()

    for makedir in makedirs:
        dir_name = PathSearcher.search(config, makedir)
        os.makedirs(dir_name, exist_ok=True)

    config = Obj(config)
    data, model, exp = config.data, config.model, config.exp
    return config, data, model, exp
