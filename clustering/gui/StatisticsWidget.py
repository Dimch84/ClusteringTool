from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout
import numpy as np

from clustering.metrics import metrics


class StatisticsWidget(QWidget):
    def __init__(self, data: np.ndarray, target: list[int], pred: list[int]):
        super().__init__()
        self.setMinimumSize(400, 700)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)

        if data is not None:
            for metric in filter(lambda m: not m.needs_target, metrics):
                layout.addRow(QLabel(metric.name), QLabel(str(metric.calc_score(data=data, pred=pred))))

        if target is not None:
            for metric in filter(lambda m: m.needs_target, metrics):
                layout.addRow(QLabel(metric.name), QLabel(str(metric.calc_score(target=target, pred=pred))))
