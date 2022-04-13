import sklearn.metrics as sm
import numpy as np
import math


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


metrics = list([sm.rand_score,
                sm.adjusted_rand_score,
                sm.fowlkes_mallows_score,
                sm.completeness_score,
                sm.calinski_harabasz_score,
                sm.silhouette_score,
                minkowski_score,
                purity_score])