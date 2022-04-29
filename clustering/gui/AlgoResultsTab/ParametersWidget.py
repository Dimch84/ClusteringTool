from PyQt5.QtWidgets import QWidget, QLabel, QFormLayout
import numpy as np

from clustering.scores import scores


class ParametersWidget(QWidget):
    def __init__(self, params: dict):
        super().__init__()
        self.setMinimumSize(400, 300)
        layout = QFormLayout(self)
        layout.setVerticalSpacing(20)
        layout.setHorizontalSpacing(50)

        print(params)

        for param_name in params.keys():
            layout.addRow(QLabel(f"{param_name}: "), QLabel(str(params[param_name])))