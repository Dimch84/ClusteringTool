from collections.abc import Callable
import numpy as np
import os
import importlib


class Algorithm:
    name: str
    __run: Callable[[np.array, int], np.array]

    def __init__(self, name: str, run: Callable[[np.array, int], np.array]):
        self.name = name
        self.__run = run

    # Can't pass Dataset here, because it may contain target
    def run(self, data: np.array, k: int = None) -> np.array:
        return self.__run(data, k)


def load_algorithms() -> [Algorithm]:
    res = []
    files = filter(lambda it: os.path.isfile('algorithms/' + it), os.listdir('algorithms'))
    for file in files:
        lib = importlib.import_module('clustering.algorithms.' + os.path.splitext(os.path.basename(file))[0])
        try:
            res.extend(lib.algorithms)
        except AttributeError:
            print(f"Could not find algorithms variable in file {file}, skipping")

    return res
