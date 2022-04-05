from collections.abc import Callable
import numpy as np


class Algorithm:
    name: str
    __run: Callable[[np.array, int], np.array]

    def __init__(self, name: str, run: Callable[[np.array, int], np.array]):
        self.name = name
        self.__run = run

    def run(self, data: np.array, k: int = None):
        return self.__run(data, k)