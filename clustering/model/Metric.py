from collections.abc import Callable


class Metric:
    name: str
    metric_fun: Callable

    def __init__(self, name: str, metric_fun: Callable):
        self.name = name
        self.metric_fun = metric_fun
