import random
from metrics import metrics
from PyQt5.QtCore import Qt, QPointF, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout
from PyQt5.QtGui import QTransform
import numpy as np


class StatisticsWidget(QWidget):
    def __init__(self, data: np.ndarray, target: list[int], pred: list[int]):
        super().__init__()
        self.setMinimumSize(400, 700)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)

        if not data is None:
            layout.addRow(QLabel("Silhouette:"), QLabel(str(metrics[5](data, pred))))
            layout.addRow(QLabel("Calinski-Harabasz:"), QLabel(str(metrics[4](data, pred))))

        if not target is None:
            layout.addRow(QLabel("Rand:"), QLabel(str(metrics[0](target, pred))))
            layout.addRow(QLabel("Adjusted rand:"), QLabel(str(metrics[1](target, pred))))
            layout.addRow(QLabel("Fowlkes-Mallows:"), QLabel(str(metrics[2](target, pred))))
            layout.addRow(QLabel("Completeness:"), QLabel(str(metrics[3](target, pred))))
            layout.addRow(QLabel("Minkowski:"), QLabel(str(metrics[6](target, pred))))
            layout.addRow(QLabel("Purity:"), QLabel(str(metrics[7](target, pred))))