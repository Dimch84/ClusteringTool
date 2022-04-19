from collections.abc import Callable
import sklearn.metrics as sm
import numpy as np
import math


class Metric:
    # Works with supposition that each metric either takes (data, pred) or (target, pred)
    name: str
    score_fun: Callable
    needs_target: bool

    def __init__(self, name: str, score_fun: Callable, needs_target: bool):
        self.name = name
        self.score_fun = score_fun
        self.needs_target = needs_target

    def calc_score(self, data: np.ndarray = None, target: list[int] = None, pred: list[int] = None):
        if pred is None or (self.needs_target and target is None) or (not self.needs_target and data is None):
            return None
        if self.needs_target:
            return self.score_fun(target, pred)
        return self.score_fun(data, pred)


def get_intersection_table(target: list[int], pred: list[int]):
    n = len(target)
    r = max(target) + 1
    s = max(pred) + 1
    m = np.zeros((r, s))
    for i in range(n):
        m[target[i]][pred[i]] += 1
    return m


def minkowski_score(target: list[int], pred: list[int]):
    m = get_intersection_table(target, pred)
    a = list(map(sum, m))
    b = list(map(sum, np.swapaxes(m, 0, 1)))
    sa = sum(map(lambda el: el * (el - 1) / 2, a))
    sb = sum(map(lambda el: el * (el - 1) / 2, b))
    sn = sum(map(lambda el: el * (el - 1) / 2, np.ravel(m)))
    return math.sqrt(sa + sb - 2 * sn) / math.sqrt(sb)


def purity_score(target: list[int], pred: list[int]):
    n = len(target)
    m = get_intersection_table(target, pred)
    return sum(map(max, m)) / n


metrics = [
    Metric("Rand", sm.rand_score, True),
    Metric("Adjusted rand", sm.rand_score, True),
    Metric("Fowlkes-Mallows", sm.fowlkes_mallows_score, True),
    Metric("Completeness", sm.completeness_score, True),
    Metric("Calinski-Harabasz", sm.calinski_harabasz_score, False),
    Metric("Silhouette", sm.silhouette_score, False),
    Metric("Minkowski", minkowski_score, True),
    Metric("Purity", purity_score, True)
]