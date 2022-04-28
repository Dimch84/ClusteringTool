from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout
import numpy as np

from clustering.metrics import metrics


class StatisticsWidget(QWidget):
    def __init__(self, data: np.ndarray, metric_names: set[str], target: np.ndarray, pred: np.ndarray):
        super().__init__()
        self.setMinimumSize(400, 700)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)
        metrics_dict = {metric.name: metric for metric in metrics}

        if data is not None:
            for metric_name in filter(lambda m: not metrics_dict[m].needs_target, metric_names):
                metric = metrics_dict[metric_name]
                layout.addRow(QLabel(metric_name), QLabel(str(metric.calc_score(data=data, pred=pred))))

        if target is not None:
            for metric_name in filter(lambda m: metrics_dict[m].needs_target, metric_names):
                metric = metrics_dict[metric_name]
                layout.addRow(QLabel(metric_name), QLabel(str(metric.calc_score(target=target, pred=pred))))