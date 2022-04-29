from collections.abc import Callable
import numpy as np
import os
import importlib


class Algorithm:
    """
    This class is used to represent an instance of clustering algorithm.
    """
    name: str
    __run: Callable[[np.ndarray, int], np.ndarray]

    def __init__(self, name: str, run: Callable[[np.ndarray, int], np.ndarray]):
        """
        :param name: title for algorithm
        :param run: function that implements clustering. It should take exactly two arguments: 2d-array with data
        and the number of classes
        """
        self.name = name
        self.__run = run

    # Can't pass Dataset here, because it may contain target
    def run(self, data: np.ndarray, k: int) -> np.ndarray:
        return self.__run(data, k)


def load_algorithms_from_module(file: str) -> [Algorithm]:
    lib = importlib.import_module('clustering.algorithms.' + os.path.splitext(os.path.basename(file))[0])
    return lib.algorithms


def load_algorithms() -> [Algorithm]:
    """
    This function scans all python files in ./algorithms folder.
    Each file should contain a global variable `algorithms` containing an Iterable of Algorithm with all algorithms
    defined in the file.

    :return: list with all algorithms extracted from those `algorithms` variables
    """
    res = []
    files = filter(lambda it: os.path.isfile(os.path.join('algorithms', it)), os.listdir('algorithms'))
    for file in files:
        try:
            res.extend(load_algorithms_from_module(file))
        except AttributeError:
            print(f"Could not find algorithms variable in file {file}, skipping")

    return res
