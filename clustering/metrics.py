from collections.abc import Callable
import sklearn.metrics as sm
import numpy as np
import math


class Metric:
    name: str
    metric_fun: Callable

    def __init__(self, name: str, metric_fun: Callable):
        self.name = name
        self.metric_fun = metric_fun


metrics = [
    Metric("Euclidean", sm._dist_metrics.EuclideanDistance),
    Metric("Manhattan", sm._dist_metrics.ManhattanDistance),
    Metric("Hamming", sm._dist_metrics.HammingDistance),
    Metric("Jaccard", sm._dist_metrics.JaccardDistance),
    Metric("Minkowski", sm._dist_metrics.MinkowskiDistance)
]
