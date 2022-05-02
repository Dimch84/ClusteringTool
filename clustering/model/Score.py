from collections.abc import Callable
import numpy as np


class Score:
    # Works with supposition that each score either takes (data, pred) or (target, pred)
    name: str
    score_fun: Callable
    needs_target: bool

    def __init__(self, name: str, score_fun: Callable, needs_target: bool):
        self.name = name
        self.score_fun = score_fun
        self.needs_target = needs_target

    def calc_score(self, data: np.ndarray = None, target: np.ndarray = None, pred: np.ndarray = None):
        if pred is None or (self.needs_target and target is None) or (not self.needs_target and data is None):
            return None
        if self.needs_target:
            return self.score_fun(target, pred)
        return self.score_fun(data, pred)
